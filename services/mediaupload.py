import os
from dotenv import load_dotenv
import boto3
from botocore.client import Config as BConfig

load_dotenv()

class MediaUpload:
    def upload(self, paths):
        account_id = os.getenv("R2_ACCOUNT_ID")
        bucket     = os.getenv("R2_BUCKET")
        key_id     = os.getenv("R2_ACCESS_KEY_ID")
        secret     = os.getenv("R2_SECRET_ACCESS_KEY")

        endpoint = f"https://{account_id}.r2.cloudflarestorage.com/"

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=key_id,
            aws_secret_access_key=secret,
            config=BConfig(signature_version="s3v4"),
            region_name="auto"
        )

        # Upload a file
        #file_path = "path/to/local-file.txt"
        #object_name = "uploads/local-file.txt"
        for path in paths:
            file_path = path
            #object_name =
            try:
                client.upload_file(file_path, bucket, file_path)
                print(f"Uploaded {file_path} → s3://{bucket}/{file_path}")
                return
            except Exception as e:
                print("Upload failed:", e)