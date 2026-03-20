from uuid import UUID
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import Tuple, Optional
import logging

from ..utils.s3_utils import save_file_to_s3, download_file_from_s3

from common.models_schemas.models import JobDescription
from common.models_schemas.schemas.file_wrapper import FileWrapper

logger = logging.getLogger(__name__)

async def store_job_description(
    job_id: UUID, uploaded_file: UploadFile, db: Session
) -> Tuple[str, str]:
    """
    Upload file to S3, replace any existing JobDescription row for this job_id, return (url, filename).
    """
    file_contents = await uploaded_file.read()
    raw_name = uploaded_file.filename or "upload.bin"

    s3_file_name = f"uploads/{job_id}_{raw_name}"
    s3_url = await save_file_to_s3(file_contents, s3_file_name)

    document = JobDescription(
        job_id=job_id,
        file_url=s3_url,
        file_name=raw_name,
    )
    try:
        existing = db.query(JobDescription).filter_by(job_id=job_id).first()
        if existing:
            db.delete(existing)
            db.flush()
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise

    return s3_url, raw_name


async def retrieve_job_description_file_name(
    job_id: UUID, db_session: Session
) -> Optional[str]:
    try:
        job_description = (
            db_session.query(JobDescription)
            .filter(JobDescription.job_id == job_id)
            .one_or_none()
        )
        if job_description:
            file_name: str = job_description.file_name
            logger.info("Retrieved file_name for job_id=%s", job_id)
            return file_name
        return None
    except Exception:
        logger.exception("Error retrieving job description file name for job_id=%s", job_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving job description file name",
        )


async def retrieve_job_description_file(
    job_id: UUID,
    db_session: Session,
) -> FileWrapper:
    doc_record = (
        db_session.query(JobDescription)
        .filter(JobDescription.job_id == job_id)
        .one_or_none()
    )
    if doc_record is None:
        logger.warning("No job description found for job_id=%s", job_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    file_url = doc_record.file_url
    file: FileWrapper = await download_file_from_s3(file_url)
    return file