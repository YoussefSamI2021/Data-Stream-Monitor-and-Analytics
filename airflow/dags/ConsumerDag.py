import sys
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.datasets import Dataset
from datetime import datetime, timedelta
from configs.kafka_conf import kafka_kwargs, Schema_STR
from airflow.utils.dates import days_ago
from models.s3_model import S3Client
from models.kafka_model import send_data_to_kafka
from configs.s3_conf import S3_BUCKET_NAME, S3_FILE_NAME, LOCAL_FILE_PATH

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

default_args = {
    'owner': 'Youssef Samy',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

data = Dataset(f"s3://{S3_BUCKET_NAME}/{S3_FILE_NAME}")

with DAG(
    's3_to_kafka_v4',
    default_args=default_args,
    description='Fetch CSV from S3 and send to Kafka as JSON',
    schedule=data,
) as dag:


    download_task = PythonOperator(
        task_id='download_s3_data',
        python_callable=S3Client.download_data_from_s3,
        op_kwargs={
            'file_path': 'Raw_data.csv',
            'bucket_name': S3_BUCKET_NAME,
            's3_key': S3_FILE_NAME
        }
    )

    kafka_task = PythonOperator(
        task_id='send_to_kafka',
        python_callable=send_data_to_kafka,
        op_kwargs={
            'file_path': 'Raw_data.csv',
            'topic': 'Data_Source_v2',
            'schema_str': Schema_STR,
            'kafka_args': kafka_kwargs
        }
    )

    download_task >> kafka_task
