# to run this job should be add a parameter in job parameter "--additional-python-modules psycopg2-binary"
# In the Job parameters section, you will see fields for adding key-value pairs.
# In the Key field, enter --additional-python-modules.
# In the Value field, enter psycopg2-binary.


import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, year, month, dayofmonth,dayofweek, dayofyear, weekofyear, quarter, first, last, date_format, to_date, current_date, sequence

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql import SparkSession


# Read data from s3

customer_df = spark.read.parquet("s3://cleaned-ecommerc-data-iti/customers/cleaning-customers-job_19Sep2024_1726737754789/")
order_df = spark.read.parquet("s3://cleaned-ecommerc-data-iti/orders/cleaning-orders-job_19Sep2024_1726737530862/")
payment_df = spark.read.parquet("s3://cleaned-ecommerc-data-iti/payments/cleaning-payments-job_19Sep2024_1726738451011/")
product_df = spark.read.parquet("s3://cleaned-ecommerc-data-iti/products/cleaning-products-job_19Sep2024_1726741513674/")

# Create Date dim
# Define start date (2010-01-01)
start_date = "2010-01-01"

# Create a DataFrame with a sequence of dates
df = spark.createDataFrame([(start_date,)], ["start_date"]) \
    .withColumn("start_date", to_date(col("start_date"))) \
    .withColumn("end_date", current_date()) \
    .withColumn("date_sequence", sequence(col("start_date"), col("end_date")))

# Explode the sequence to get a row per date
df = df.selectExpr("explode(date_sequence) as date")

# Add additional columns to create the dates_dim_df
dates_dim_df = df \
    .withColumn('date_id', F.date_format(df["date"], "yyyyMMdd")) \
    .withColumn('weekday', F.date_format('date', 'EEEE')) \
    .withColumn('day_of_week_num', F.dayofweek('date')) \
    .withColumn('day_month', F.dayofmonth('date')) \
    .withColumn('day_of_year', F.dayofyear('date')) \
    .withColumn('week_of_year', F.weekofyear('date')) \
    .withColumn('month_num', F.month('date')) \
    .withColumn('month_name', F.date_format('date', 'MMMM')) \
    .withColumn('quarter', F.quarter('date')) \
    .withColumn('year', F.year('date')) \
  

# Show the first few rows of the extended dates dimension table
# dates_dim_df.display()

# Join Orders Fact Table with Payments Dimension Table
payment_dim_df = order_df.alias("o") \
    .join(payment_df.alias("p"), col("o.order_id") == col("p.order_id"), "inner") \
    .select('payment_id', 'payment_date_id', 'amount', 'payment_method')


# Join Orders Fact Table with Payments Dimension Table
orders_fact_df = order_df.alias("o") \
    .join(payment_df.alias("p"), col("o.order_id") == col("p.order_id"), "inner") \
    .select("o.order_id", "o.customer_id","p.payment_id", "o.order_date_id", "o.total_amount")

from pyspark.sql import Row
import random
# Simulating the Order-Product relationship (many-to-many)

order_ids = [row['order_id'] for row in orders_fact_df.collect()]
product_ids = [row['product_id'] for row in product_df.collect()]

# Generating random associations between orders and products (many-to-many)
order_product_data = []
for order_id in order_ids:
    num_products = random.randint(1, 3)  # Each order can have 1 to 3 products
    selected_products = random.sample(product_ids, num_products)
    for product_id in selected_products:
        order_product_data.append((order_id, product_id))

# Creating the Order-Product DataFrame
order_product_columns = ['order_id', 'product_id']
order_product_df = spark.createDataFrame(order_product_data, schema=order_product_columns)
order_product_df = order_product_df \
    .withColumnRenamed("order_id", "order_id_op")


# Join the Order-Product table with the Fact table
orders_fact_df = orders_fact_df.alias("o") \
    .join(order_product_df.alias("op"), col("o.order_id") == col("op.order_id_op"), "inner").drop("order_id_op")


product_dim_df = product_df

customer_dim_df = customer_df

# Define the S3 bucket and path where you want to save the DataFrames
s3_bucket = "s3://star-schema-bucket/"
s3_orders_fact_path = s3_bucket + "orders_fact/"
s3_product_dim_path = s3_bucket + "product_dim/"
s3_customer_dim_path = s3_bucket + "customer_dim/"
s3_payment_dim_path = s3_bucket + "payment_dim/"
s3_dates_dim_path = s3_bucket + "dates_dim/"

# Save each DataFrame as Parquet files
orders_fact_df.write.mode("overwrite").parquet(s3_orders_fact_path)
product_dim_df.write.mode("overwrite").parquet(s3_product_dim_path)
customer_dim_df.write.mode("overwrite").parquet(s3_customer_dim_path)
payment_dim_df.write.mode("overwrite").parquet(s3_payment_dim_path)
dates_dim_df.write.mode("overwrite").parquet(s3_dates_dim_path)

#tables=[orders_fact_df,product_dim_df,customer_dim_df,payment_dim_df,dates_dim_df]
orders_fact_df = spark.read.parquet("s3://star-schema-bucket/orders_fact/")
product_dim_df = spark.read.parquet("s3://star-schema-bucket/product_dim/")
customer_dim_df = spark.read.parquet("s3://star-schema-bucket/customer_dim/")
payment_dim_df = spark.read.parquet("s3://star-schema-bucket/payment_dim/")
dates_dim_df = spark.read.parquet("s3://star-schema-bucket/dates_dim/")



import psycopg2

# Redshift connection details
redshift_host = "default-workgroup.612140784837.us-east-1.redshift-serverless.amazonaws.com"
redshift_port = "5439"
redshift_db = "dev"
redshift_user = "admin"
redshift_password = "Admin1234"

# S3 paths for the DataFrames
s3_bucket = "s3://star-schema-bucket/"
s3_orders_fact_path = s3_bucket + "orders_fact/"
s3_product_dim_path = s3_bucket + "product_dim/"
s3_customer_dim_path = s3_bucket + "customer_dim/"
s3_payment_dim_path = s3_bucket + "payment_dim/"
s3_dates_dim_path = s3_bucket + "dates_dim/"

# Connect to Redshift
conn = psycopg2.connect(
    dbname=redshift_db,
    user=redshift_user,
    password=redshift_password,
    host=redshift_host,
    port=redshift_port
)
cursor = conn.cursor()


# Redshift IAM Role ARN (if applicable)
iam_role = "arn:aws:iam::612140784837:role/service-role/AmazonRedshift-CommandsAccessRole-20240921T045807"

# Copy commands for each table
copy_commands = [
    f"""
    COPY orders_fact_df
    FROM '{s3_orders_fact_path}'
    IAM_ROLE '{iam_role}'
    FORMAT AS PARQUET;
    """,
    f"""
    COPY product_dim_df
    FROM '{s3_product_dim_path}'
    IAM_ROLE '{iam_role}'
    FORMAT AS PARQUET;
    """,
    f"""
    COPY customer_dim_df
    FROM '{s3_customer_dim_path}'
    IAM_ROLE '{iam_role}'
    FORMAT AS PARQUET;
    """,
    f"""
    COPY payment_dim_df
    FROM '{s3_payment_dim_path}'
    IAM_ROLE '{iam_role}'
    FORMAT AS PARQUET;
    """,
    f"""
    COPY dates_dim_df
    FROM '{s3_dates_dim_path}'
    IAM_ROLE '{iam_role}'
    FORMAT AS PARQUET;
    """
]

# Execute each COPY command
for command in copy_commands:
    try:
        cursor.execute(command)
        conn.commit()
        print("Data copied successfully.")
    except Exception as e:
        print(f"Error while copying data: {str(e)}")
        conn.rollback()

# Close the connection
cursor.close()
conn.close()


job.commit()