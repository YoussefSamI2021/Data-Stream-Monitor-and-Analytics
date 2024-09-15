import pyspark.sql.functions as F
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col, when, regexp_extract, date_format
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
        """Read data from Kafka topic"""
        return self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_config.bootstrap_servers) \
            .option("subscribe", self.kafka_config.topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", False) \
            .option("spark.streaming.kafka.maxRatePerPartition", "50") \
            .load()

    def process_data(self):
        """Process incoming data from Kafka and write to S3"""
        kafka_df = self.read_from_kafka()
        schema_str = SchemaRegistryUtil.get_avro_schema(self.kafka_config)

        kafka_df = kafka_df.withColumn('fixedValue', F.expr("substring(value, 6, length(value)-5)"))

        from_avro_options = {"mode": "PERMISSIVE"}
        decoded_df = kafka_df.select(
            from_avro(F.col("fixedValue"), schema_str, from_avro_options).alias("data_source")
        )
        kafka_value_df = decoded_df.select("data_source.*")
        kafka_value_df.printSchema()

        # Data transformations
        cleaned_df = self.transform_data(kafka_value_df)
        self.write_to_s3(cleaned_df)


    def transform_data(self, df):
        """Apply data transformations"""
        df = df.dropna(subset=["Courier_Status"]).dropDuplicates()
        df = df.withColumn(
            "formatted_date", 
            when(col("Date.member1").isNotNull(), date_format(col("Date.member1"), "yyyyMMdd"))
            .otherwise("not_available")
        )
        pattern = r'^(\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+)'
        df = df.withColumn(
            "promotion_ids", regexp_extract("promotion_ids", pattern, 1)
        ).na.fill({"promotion_ids": "not_available"})
        return df

    def write_to_s3(self, df):
        """Write the processed data to S3 in parquet format"""
        df.writeStream \
            .format("parquet") \
            .outputMode("append") \
            .trigger(processingTime='1 second') \
            .option("path", self.s3_config.bucket_path + "/test") \
            .option("checkpointLocation", self.s3_config.checkpoint_path+'test') \
            .start() \
            .awaitTermination()
