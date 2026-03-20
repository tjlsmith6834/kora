import os
import urllib
from sqlalchemy.orm import Session
from typing import List
import boto3
from botocore.exceptions import NoCredentialsError
import io
from uuid import UUID
import logging

from common.models_schemas.models import ApplicationDocuments

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

class FileWrapper(io.BytesIO):
    def __init__(self, file_bytes: bytes, name: str):
        super().__init__(file_bytes)
        self.name = name

    @property
    def file(self):
        return self

async def retrieve_application_docs(
    application_id: UUID,
    db_session: Session,
    bucket_name: str = "hiring-platform-dev-bucket"
) -> List[FileWrapper]:
    """
    Retrieves documents from S3 for a given application.

    Returns:
        List[FileWrapper]: A list of file-like objects with a .name attribute.
    """
    docs = db_session.query(ApplicationDocuments).filter(
        ApplicationDocuments.application_id == application_id
    ).all()

    if not docs:
        logging.warning(f"No documents found for application_id: {application_id}")
        return []

    results = []
    for doc in docs:
        file_url = doc.file_url
        try:
            parsed_url = urllib.parse.urlparse(file_url)
            s3_key = parsed_url.path.lstrip("/")
            response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
            file_data = response["Body"].read()
            file_name = s3_key.split("/")[-1]
            wrapped_file = FileWrapper(file_data, file_name)
            results.append(wrapped_file)
            logging.info(f"Successfully retrieved {file_name} from S3.")
        except NoCredentialsError:
            logging.error("AWS credentials not found.")
            continue
        except Exception as e:
            logging.error(f"Error retrieving {file_url} from S3: {e}")
            continue

    return results

async def retrieve_primary_resume(
    application_id: UUID,
    db_session: Session,
    bucket_name: str = "hiring-platform-dev-bucket"
) -> FileWrapper | None:
    """
    Retrieves *just* the primary resume document from S3 for a given application.
    Returns a FileWrapper if found, or None if no primary resume is marked.
    """
    # only pull the doc whose `is_primaryresume` flag is True
    doc: ApplicationDocuments | None = (
        db_session
        .query(ApplicationDocuments)
        .filter(
            ApplicationDocuments.application_id == application_id,
            ApplicationDocuments.is_primary_resume.is_(True)
        )
        .one_or_none()
    )

    if not doc:
        logging.warning(f"No primary resume found for application_id: {application_id}")
        return None

    file_url = doc.file_url
    try:
        parsed = urllib.parse.urlparse(file_url)
        s3_key = parsed.path.lstrip("/")
        resp = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        data = resp["Body"].read()
        name = s3_key.split("/")[-1]
        logging.info(f"Successfully retrieved primary resume {name} from S3.")
        return FileWrapper(data, name)

    except NoCredentialsError:
        logging.error("AWS credentials not found.")
    except Exception as e:
        logging.error(f"Error retrieving {file_url} from S3: {e}")

    return None