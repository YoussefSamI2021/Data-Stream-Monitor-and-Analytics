import os
class S3Config:
    def __init__(self, bucket_path, checkpoint_path):
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_path = bucket_path
        self.checkpoint_path = checkpoint_path
