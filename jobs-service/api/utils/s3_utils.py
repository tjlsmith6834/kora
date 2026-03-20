import os
import boto3
import io
from botocore.exceptions import NoCredentialsError
import urllib
from urllib.parse import urlparse
import logging
import asyncio


from common.models_schemas.schemas.file_wrapper import FileWrapper

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


async def save_file_to_s3(
        file_contents: bytes,
        file_name: str,
        bucket_name: str = "hiring-platform-dev-bucket"
) -> str:
    """
    Save the file to an S3 bucket and return the file URL.
    """
    try:
        logging.info(f"Uploading file to S3 as {file_name}")

        # Upload the file to S3
        s3_client.upload_fileobj(io.BytesIO(file_contents), bucket_name, file_name)

        # Construct the file URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        logging.info(f"File uploaded successfully to {file_url}")
        return file_url
    except NoCredentialsError as e:
        logging.error(f"AWS credentials not found: {e}")
        raise Exception("Failed to upload file to S3 due to missing credentials")
    except Exception as e:
        logging.error(f"An error occurred during S3 upload: {e}")
        raise

async def delete_file_from_s3(
        file_url: str
):
    parsed = urlparse(file_url)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    s3_client.delete_object(Bucket=bucket, Key=key)


async def download_file_from_s3(
    file_url: str,
    bucket_name: str = "hiring-platform-dev-bucket"
) -> FileWrapper:
    parsed = urllib.parse.urlparse(file_url)
    key = parsed.path.lstrip("/")

    # run the blocking S3 call in a thread
    response = await asyncio.to_thread(
        s3_client.get_object,
        Bucket=bucket_name,
        Key=key
    )

    body_bytes = await asyncio.to_thread(response["Body"].read)

    filename = key.rsplit("/", 1)[-1]

    file_wrapper = FileWrapper(body_bytes, filename)
    return file_wrapper