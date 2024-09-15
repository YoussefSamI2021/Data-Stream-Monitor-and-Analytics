import time
from config.kafka_config import KafkaConfig
from config.s3_config import S3Config
from config.spark_config import SparkConfig
from processors.data_processor import DataProcessor
from pyspark.sql import SparkSession

if __name__ == "__main__":
    print("Data Processing Application Started at:", time.strftime("%Y-%m-%d %H:%M:%S"))

    # Kafka and Schema Registry Configurations
    kafka_config = KafkaConfig(
        topic="Data_Source_v2",
        bootstrap_servers="18.189.79.27:9092,18.189.79.27:9093,18.189.79.27:9094",
        schema_registry_url="http://18.189.79.27:8081",
        schema_subject="Data_Source_v2"
    )

    # S3 Configurations
    s3_config = S3Config(
        access_key="AKIAY5BTPDTCYOVIKYP3",
        secret_key="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",
        bucket_path="s3a://dest-data-lake-iti",
        checkpoint_path="s3a://dest-data-lake-iti/chkpoint-1"
    )

    # Spark Configurations
    spark_config = SparkConfig()

    # Initialize Spark Session
    spark = SparkSession.builder.config(conf=spark_config.conf).getOrCreate()

    # Initialize and run the data processing
    processor = DataProcessor(kafka_config, s3_config, spark)
    processor.process_data()
