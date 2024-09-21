import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.dates import days_ago
from confluent_kafka.avro import AvroProducer
from airflow.datasets import Dataset
from configs.kafka_conf import CONFIG
from configs.s3_conf import S3_BUCKET_NAME, BASE_DIR , AWS_CONN
from datetime import  timedelta
import json 
import time
from schemas.customer_schema import customer_avro_schema , key_customer_schema
from schemas.orders_schema import orders_avro_schema , key_orders_schema
from schemas.payments_schema import payments_avro_schema , key_payments_schema
from schemas.products_schema import products_avro_schema ,key_products_schema

# Configuration
data = Dataset(f"s3://{S3_BUCKET_NAME}/{BASE_DIR}")

# Kafka topic mapping per dataset
KAFKA_TOPICS = {
    'customers': 'customers_topic',
    'orders': 'orders_topic',
    'payments': 'payments_topic',
    'products': 'products_topic'
}

# Avro schema mapping per dataset
AVRO_SCHEMAS = {
    'customers': customer_avro_schema,
    'orders': orders_avro_schema,
    'payments': payments_avro_schema,
    'products': products_avro_schema
}

# Function to list the latest file from an S3 directory
def get_latest_generation_file(s3_path, **kwargs):
    s3 = S3Hook(aws_conn_id=AWS_CONN)
    files = s3.list_keys(bucket_name=S3_BUCKET_NAME, prefix=s3_path)

    if not files:
        raise ValueError(f"No files found in {s3_path}")

    # Assuming files are in the format like 'customers/customers_g1.csv'
    files_sorted = sorted(files, key=lambda x: int(x.split('_g')[1].split('.')[0]), reverse=True)
    latest_file = files_sorted[0]
    return latest_file

# Function to read a CSV file from S3 and return as a DataFrame
def read_csv_from_s3(key):
    s3 = S3Hook(aws_conn_id=AWS_CONN)
    file_obj = s3.get_key(key, bucket_name=S3_BUCKET_NAME)
    data = pd.read_csv(file_obj.get()['Body'])
    return data

# Function to send data to Kafka using Avro schema
def send_to_kafka(data, dataset_key ,key_schema):
    key_schemas = json.dumps(key_schema)
    value_schema = json.dumps(AVRO_SCHEMAS[dataset_key])
    avro_producer = AvroProducer({
        'bootstrap.servers': CONFIG['bootstrap_servers'],
        'schema.registry.url': CONFIG['schema_registry_url'],
    }, 
    default_key_schema=key_schemas,
    default_value_schema=value_schema)
    topic = KAFKA_TOPICS[dataset_key]

    for index, row in data.iterrows():
        # print(row)
        avro_producer.produce(
            topic=topic,
            key=None,  # Use row index as key, or adjust if needed
            value=row.to_dict()  # Data is serialized using Avro schema
        )
        time.sleep(0.01)
    
    avro_producer.flush()

# Main task function to get the latest data and send to Kafka
def process_and_send_data(**context):
    # Fetch the latest files from each directory
    latest_customers = get_latest_generation_file(f'{BASE_DIR}/customers')
    latest_orders = get_latest_generation_file(f'{BASE_DIR}/orders')
    latest_payments = get_latest_generation_file(f'{BASE_DIR}/payments')
    latest_products = get_latest_generation_file(f'{BASE_DIR}/products')

    # Read the latest files into DataFrames
    customers_df = read_csv_from_s3(latest_customers)
    orders_df = read_csv_from_s3(latest_orders)
    payments_df = read_csv_from_s3(latest_payments)
    products_df = read_csv_from_s3(latest_products)

    # Send data to Kafka with specific topics
    send_to_kafka(customers_df, 'customers' , key_customer_schema)
    send_to_kafka(orders_df, 'orders' , key_orders_schema)
    send_to_kafka(payments_df, 'payments' , key_payments_schema)
    send_to_kafka(products_df, 'products' , key_products_schema)

# Airflow DAG configuration
default_args = {
    'owner': 'Youssef Samy',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

with DAG(
    'ecommerce_data_consumer_with_schemas',
    default_args=default_args,
    description='Consume and send latest e-commerce data from S3 to Kafka with Avro schemas',
    schedule=data,
    catchup=False,
) as dag:

    process_data = PythonOperator(
        task_id='process_and_send_data',
        python_callable=process_and_send_data,
        provide_context=True
    )
    
    process_data
