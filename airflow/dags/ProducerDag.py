from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.datasets import Dataset
from configs.s3_conf import S3_BUCKET_NAME, S3_FILE_NAME , AWS_CONN
from models.s3_operations import S3DataProcessor

default_args = {
    'owner': 'Youssef Samy',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

s3_processor = S3DataProcessor(aws_conn_id=AWS_CONN)

data = Dataset(f"s3://{S3_BUCKET_NAME}/{S3_FILE_NAME}")

with DAG(
    'producer_data_to_s3',
    default_args=default_args,
    description='Upload dataset in batches to S3',
    schedule='@daily',
    catchup=False
) as dag:

    get_last_index = PythonOperator(
        task_id='get_last_index',
        python_callable=s3_processor.get_last_processed_index,
        provide_context=True,
    )

    upload_to_s3 = PythonOperator(
        task_id='upload_to_s3',
        python_callable=s3_processor.upload_batch_to_s3,
        provide_context=True,
        op_args=['{{ ti.xcom_pull(task_ids="get_last_index") }}'],
        outlets=data,
    )

    get_last_index >> upload_to_s3
