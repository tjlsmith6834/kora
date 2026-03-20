import os
from typing import List
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session
import boto3
import logging
import requests
import cloudconvert
import re
from botocore.exceptions import NoCredentialsError
from tenacity import retry, stop_after_attempt, wait_exponential
import io

from common.models_schemas.models import ApplicationDocuments

logger = logging.getLogger(__name__)

cloudconvert.configure(api_key=os.environ["CLOUDCONVERT_API_KEY"])

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)
BUCKET_NAME = "hiring-platform-dev-bucket"
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

def safe_filename(filename: str) -> str:
    """Sanitize filename for S3 keys (no spaces or weird chars)."""
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def upload_with_retry(file_bytes: bytes, bucket: str, key: str) -> str:
    """
    Upload file bytes to S3 with retry safety.
    Returns the S3 URL of the uploaded object.
    """
    s3_client.upload_fileobj(io.BytesIO(file_bytes), bucket, key)
    return f"https://{bucket}.s3.{AWS_REGION}.amazonaws.com/{key}"


def _create_docx_to_pdf_job(presigned_url: str) -> dict:
    """Create and wait for a CloudConvert DOCX->PDF job."""
    job = cloudconvert.Job.create(payload={
        "tasks": {
            "import-my-file": {
                "operation": "import/url",
                "url": presigned_url
            },
            "convert-my-file": {
                "operation": "convert",
                "input": "import-my-file",
                "input_format": "docx",
                "output_format": "pdf",
                "engine": "libreoffice"
            },
            "export-my-file": {
                "operation": "export/url",
                "input": "convert-my-file"
            }
        }
    })
    return cloudconvert.Job.wait(id=job["id"])


def _download_converted_pdf(job: dict) -> bytes:
    """Extract export URL from a CloudConvert job and download resulting PDF bytes."""
    export_task = next(
        (t for t in job["tasks"] if t["operation"] == "export/url"),
        None
    )
    if not export_task or "result" not in export_task:
        raise RuntimeError(f"CloudConvert export task failed: {job}")

    file_url = export_task["result"]["files"][0]["url"]
    response = requests.get(file_url, timeout=60)
    response.raise_for_status()
    return response.content


async def store_uploaded_files(
    application_id: UUID,
    uploaded_files: List[UploadFile],
    db: Session,
    primary_resume: bool = False
) -> List[str]:
    s3_urls = []

    for uploaded_file in uploaded_files:
        filename = safe_filename(uploaded_file.filename or "upload.bin")
        file_ext = filename.lower().split(".")[-1]
        file_bytes = await uploaded_file.read()

        if file_ext == "docx":
            # Temporary upload of .docx for CloudConvert
            temp_key = f"temp/{application_id}_{filename}"
            upload_with_retry(file_bytes, BUCKET_NAME, temp_key)
            try:
                presigned_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": BUCKET_NAME, "Key": temp_key},
                    ExpiresIn=600  # 10 minutes
                )

                job = _create_docx_to_pdf_job(presigned_url)
                pdf_bytes = _download_converted_pdf(job)

                # Upload PDF with retry
                pdf_filename = filename.replace(".docx", ".pdf")
                pdf_key = f"uploads/{application_id}_{pdf_filename}"
                s3_url = upload_with_retry(pdf_bytes, BUCKET_NAME, pdf_key)
            finally:
                # Best-effort cleanup of temporary object.
                try:
                    s3_client.delete_object(Bucket=BUCKET_NAME, Key=temp_key)
                except Exception:
                    logger.exception("Failed to delete temporary DOCX from S3")

        else:
            # For non-docx just upload original
            s3_key = f"uploads/{application_id}_{filename}"
            s3_url = upload_with_retry(file_bytes, BUCKET_NAME, s3_key)

        # Store only the final URL (PDF or original) in DB
        document = ApplicationDocuments(
            application_id=application_id,
            file_url=s3_url,
            is_primary_resume=primary_resume,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        s3_urls.append(s3_url)

    return s3_urls

@retry(
    stop=stop_after_attempt(5),  # Retry up to 5 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
)
async def save_file_to_s3(file_contents: bytes, file_name: str, bucket_name: str = "hiring-platform-dev-bucket") -> str:
    """
    Save the file to an S3 bucket and return the file URL.
    """
    try:
        logger.info(f"Uploading file to S3 as {file_name}")

        # Upload the file to S3
        s3_client.upload_fileobj(io.BytesIO(file_contents), bucket_name, file_name)

        # Construct the file URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        logger.info(f"File uploaded successfully to {file_url}")
        return file_url
    except NoCredentialsError:
        logger.exception("AWS credentials not found")
        raise Exception("Failed to upload file to S3 due to missing credentials")
    except Exception:
        logger.exception("An error occurred during S3 upload")
        raise

