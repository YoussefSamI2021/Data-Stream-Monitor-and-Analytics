FROM apache/airflow:2.10.0-python3.10

# Switch to the airflow user to install packages
USER airflow

# Install necessary Python libraries
RUN pip install --no-cache-dir \
    kafka-python \
    pandas \
    pyodbc \
    sqlalchemy \
    boto3
