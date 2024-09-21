import pyspark.sql.functions as F
from pyspark.sql.avro.functions import from_avro
from utils.schema_registry import SchemaRegistryUtil

class DataProcessor:
    def __init__(self, kafka_config, s3_config, spark_session):
        self.kafka_config = kafka_config
        self.s3_config = s3_config
        self.spark = spark_session
        self.configure_s3(self.spark.sparkContext, s3_config)

    def configure_s3(self, spark_context, s3_config):
        """Configure S3 access in Spark"""
        hadoop_conf = spark_context._jsc.hadoopConfiguration()
        hadoop_conf.set("fs.s3a.access.key", s3_config.access_key)
        hadoop_conf.set("fs.s3a.secret.key", s3_config.secret_key)
        hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        hadoop_conf.set("fs.s3a.endpoint", "s3.amazonaws.com")
        hadoop_conf.set("fs.s3a.connection.ssl.enabled", "true")
        hadoop_conf.set("fs.s3a.path.style.access", "true")

    def read_from_kafka(self):
        """Read data from Kafka topics"""
        return self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_config.bootstrap_servers) \
            .option("subscribe", ",".join(self.kafka_config.topics)) \
            .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", False) \
            .option("spark.streaming.kafka.maxRatePerPartition", "50") \
            .load()

    def process_data(self):
        """Process incoming data from Kafka and write to S3"""
        kafka_df = self.read_from_kafka()
        queries = []

        for topic in self.kafka_config.topics:
            # Fetch Avro schema for both key and value for the current topic
            schema_value_str = SchemaRegistryUtil.get_avro_schema(self.kafka_config, topic, is_key=False)

            # Extract and decode Kafka message key and value
            from_avro_options = {"mode": "PERMISSIVE"}
            topic_df = kafka_df.filter(F.col("topic") == topic)  # Filter data per topic

            topic_df = topic_df.withColumn('fixedValue', F.expr("substring(value, 6, length(value)-5)"))
            # topic_df = topic_df.withColumn('fixedKey', F.expr("substring(key, 6, length(key)-5)"))

            decoded_df = topic_df.select(
                # from_avro(F.col("fixedKey"), schema_key_str, from_avro_options).alias("key_data"),
                from_avro(F.col("fixedValue"), schema_value_str, from_avro_options).alias("value_data")
            )

            # topic_value_df = decoded_df.select("key_data.*", "value_data.*")
            topic_value_df = decoded_df.select("value_data.*")
            topic_value_df.printSchema()

            # Write data to S3 and start streaming queries
            query = self.write_to_s3(topic_value_df, topic)
            queries.append(query)

        # Await termination of all queries
        for query in queries:
            query.awaitTermination()

    def write_to_s3(self, df, topic):
        """Write the processed data to S3 in parquet format"""
        return df.writeStream \
            .format("parquet") \
            .outputMode("append") \
            .option("path", f"{self.s3_config.bucket_path}/Staging/{topic}") \
            .start()
