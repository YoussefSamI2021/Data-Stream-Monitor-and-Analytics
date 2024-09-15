from airflow.hooks.base_hook import BaseHook
import boto3
from configs.s3_conf import AWS_CONN


class S3Client:

    @staticmethod
    def connect_to_s3(aws_conn_id):
        conn = BaseHook.get_connection(aws_conn_id)
        session = boto3.Session(
            aws_access_key_id=conn.login,
            aws_secret_access_key=conn.password,
            region_name=conn.extra_dejson.get('region_name', 'us-east-1')
        )
        if session:
            print("Connection successful")
            return session 
        return "Connection failed"

    @staticmethod
    def download_data_from_s3(file_path, bucket_name, s3_key):
        session = AWS_CONN
        conn = BaseHook.get_connection(session)
        session = boto3.Session(
            aws_access_key_id=conn.login,
            aws_secret_access_key=conn.password,
            region_name=conn.extra_dejson.get('region_name', 'us-east-1')
        )
        s3 = session.client('s3')
        with open(file_path, 'wb') as f:
            s3.download_fileobj(bucket_name, s3_key, f)
        return "File downloaded"
