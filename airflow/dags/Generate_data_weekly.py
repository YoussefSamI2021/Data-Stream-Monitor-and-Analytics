from airflow.models import Variable
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.dates import days_ago
from airflow.datasets import Dataset
from configs.s3_conf import S3_BUCKET_NAME, AWS_CONN, BASE_DIR
from datetime import timedelta
import random
import pandas as pd
import uuid
from faker import Faker
from datetime import timedelta

# Initialize Faker to generate realistic names and addresses
fake = Faker()
data = Dataset(f"s3://{S3_BUCKET_NAME}/{BASE_DIR}")

# Function to increment file number using Airflow Variable
def increment_file_number():
    # Retrieve the current file number from Airflow Variables (or set it to 1 if not exists)
    file_num = Variable.get('generate_file_num', default_var=1)
    
    # Increment the file number
    file_num = int(file_num) + 1
    
    # Update the Airflow Variable with the new file number
    Variable.set('generate_file_num', file_num)
    
    # Return the incremented file number
    return file_num

# Function to generate and save data to S3
def generate_and_save_data(**context):
    # Get the incremented file number from Airflow Variable
    file_num = Variable.get('generate_file_num', default_var=1)

    # Generate all datasets
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers, products)
    payments = generate_payments(orders)

    # Save each dataset to S3
    save_to_s3(customers, "customers", file_num, **context)
    save_to_s3(products, "products", file_num, **context)
    save_to_s3(orders, "orders", file_num, **context)
    save_to_s3(payments, "payments", file_num, **context)

# Function to generate customer data (same as before)
def generate_customers(num_customers=10000):
    customers = []
    for _ in range(num_customers):
        customer_id = str(uuid.uuid4())
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        address = fake.address().replace("\n", ", ")
        signup_date = fake.date_between(start_date="-10y", end_date="today")
        customers.append([customer_id, name, email, phone, address, signup_date])
    return pd.DataFrame(customers, columns=['customer_id', 'name', 'email', 'phone', 'address', 'signup_date'])

# Function to generate product data
def generate_products(num_products=10000):
    products = []
    categories = ['Electronics', 'Clothing', 'Home', 'Beauty', 'Toys', 'Books']
    for _ in range(num_products):
        product_id = str(uuid.uuid4())
        name = fake.word().capitalize() + ' ' + random.choice(['Gadget', 'Item', 'Accessory', 'Tool'])
        category = random.choice(categories)
        price = round(random.uniform(10, 1000), 2)
        products.append([product_id, name, category, price])
    return pd.DataFrame(products, columns=['product_id', 'name', 'category', 'price'])

# Function to generate order data
def generate_orders(customers, products, num_orders=10000):
    orders = []
    for _ in range(num_orders):
        order_id = str(uuid.uuid4())
        customer_id = random.choice(customers['customer_id'].tolist())
        order_date = fake.date_between(start_date="-10y", end_date="today")
        total_amount = 0
        for _ in range(random.randint(1, 5)):  # Between 1 to 5 items per order
            product = products.sample(1).iloc[0]
            quantity = random.randint(1, 3)
            total_amount += product['price'] * quantity
        orders.append([order_id, customer_id, order_date, total_amount])
    return pd.DataFrame(orders, columns=['order_id', 'customer_id', 'order_date', 'total_amount'])

# Function to generate payment data
def generate_payments(orders):
    payments = []
    for _, row in orders.iterrows():
        payment_id = str(uuid.uuid4())
        order_id = row['order_id']
        payment_date = row['order_date'] + timedelta(days=random.randint(0, 2))
        payment_method = random.choice(['Credit Card', 'PayPal', 'Bank Transfer'])
        payments.append([payment_id, order_id, payment_date, payment_method, row['total_amount']])
    return pd.DataFrame(payments, columns=['payment_id', 'order_id', 'payment_date', 'payment_method', 'amount'])

# Function to save data to S3 (same as before)
def save_to_s3(df, dept_name, file_num, **context):
    s3 = S3Hook(aws_conn_id=AWS_CONN)  # Airflow connection for AWS
    filename = f"{dept_name}_g{file_num}.csv"
    key = f"{BASE_DIR}/{dept_name}/{filename}"

    # Convert DataFrame to CSV and save to S3
    csv_data = df.to_csv(index=False)
    s3.load_string(string_data=csv_data, key=key, bucket_name=S3_BUCKET_NAME, replace=True)

# Airflow DAG configuration (same as before)
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
    'ecommerce_data_generation',
    default_args=default_args,
    description='Generate and save e-commerce data to S3',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task 1: Increment file number using Airflow Variables
    t1 = PythonOperator(
        task_id='increment_file_number',
        python_callable=increment_file_number
    )

    # Task 2: Generate and Save Data to S3
    t2 = PythonOperator(
        task_id='generate_and_save_data',
        python_callable=generate_and_save_data,
        provide_context=True,
        outlets=data
    )

    t1 >> t2



