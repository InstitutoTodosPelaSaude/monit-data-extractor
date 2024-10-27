import os
from minio import Minio
from minio.error import S3Error
import io

def get_minio_client():

    # Get environment variables
    endpoint   = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")

    if not endpoint or not access_key or not secret_key:
        return None

    try:
        # Initialize MinIO client
        minio_client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        # Perform a basic check, e.g., list buckets
        minio_client.list_buckets()
        return minio_client
    except S3Error as err:
        return None
    
def upload_file_to_folder(client, bucket, filename, file_content, length):
    try:
        client.put_object(
            bucket,
            filename,
            file_content,
            length
        )
        
        return True, "OK"
    except Exception as e:
        return False, str(e)
