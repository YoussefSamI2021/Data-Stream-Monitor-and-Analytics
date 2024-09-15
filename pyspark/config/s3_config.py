class S3Config:
    def __init__(self, access_key, secret_key, bucket_path, checkpoint_path):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_path = bucket_path
        self.checkpoint_path = checkpoint_path
