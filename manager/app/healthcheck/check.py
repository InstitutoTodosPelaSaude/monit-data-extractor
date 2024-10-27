import os
import sys
from minio import Minio
from minio.error import S3Error

def check_minio():
    """
    Test connection to MinIO storage.
    """

    # Get environment variables
    endpoint   = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")

    if not endpoint or not access_key or not secret_key:
        return False, "Missing one or more required MinIO environment variables (MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY). Check the .env file."

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
        return True, "MinIO connection successful."
    except S3Error as err:
        return False, f"MinIO connection failed: {err}"


def healthcheck():
    # Run multiple health checks
    checks = {
        "MinIO Check": check_minio    
    }

    all_healthy = True
    for name, check in checks.items():
        healthy, message = check()
        if not healthy:
            print(f"{name} FAILED: {message}")
            all_healthy = False
        else:
            print(f"{name}: {message}")

    if all_healthy:
        sys.exit(0)  # Healthy
    else:
        sys.exit(1)  # Unhealthy

if __name__ == "__main__":
    healthcheck()