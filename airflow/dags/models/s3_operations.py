import pandas as pd
import os
from configs.s3_conf import LOCAL_FILE_PATH, S3_BUCKET_NAME, S3_FILE_NAME, AWS_CONN, ROWS_PER_BATCH
from models.s3_model import S3Client

class S3DataProcessor:
    def __init__(self, aws_conn_id: str):
        self.s3_client = S3Client.connect_to_s3(aws_conn_id=aws_conn_id)

    def upload_batch_to_s3(self, last_index, **context):
        last_index = int(last_index)

        # Read the CSV file without setting an index
        df = pd.read_csv(LOCAL_FILE_PATH)

        # Add a new column with row indices
        df['index'] = df.index

        if last_index >= len(df):
            raise ValueError("last_index is out of bounds for the DataFrame")

        end_index = min(last_index + ROWS_PER_BATCH, len(df))
        batch_df = df.loc[last_index:end_index - 1]
        
        # Temporary file path
        temp_file_path = f'/tmp/amazon_sale_report_{last_index}_{end_index - 1}.csv'
        batch_df.to_csv(temp_file_path, index=False)
        
        # Upload to S3
        s3 = self.s3_client.client('s3')
        s3.upload_file(temp_file_path, S3_BUCKET_NAME, S3_FILE_NAME, ExtraArgs={'ContentType': 'text/csv'})
        
        # Remove the temporary file
        os.remove(temp_file_path)
        
        # Push the next index to XCom
        next_index = end_index
        if 'ti' in context:
            context['ti'].xcom_push(key='last_index', value=next_index)
        else:
            raise KeyError("Key 'ti' not found in context")

    def get_last_processed_index(self, **context):
        if 'ti' in context:
            last_index = context['ti'].xcom_pull(key='last_index', task_ids='upload_to_s3')
            return last_index if last_index is not None else 0
        else:
            raise KeyError("Key 'ti' not found in context")
