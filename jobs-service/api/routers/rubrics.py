from fastapi import APIRouter, Path, HTTPException, Depends
from sqlalchemy.orm import Session
import asyncio
from uuid import UUID
import logging

from ..services.job_descriptions import retrieve_job_description_file

from common.utils.text_from_file_utils import extract_text_from_file
from common.models_schemas.schemas.task import Task
from common.celery_config import celery_app
from common.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs/rubrics",
    tags=["Rubrics"],
)

@router.post(
    "/{job_id}",
    response_model=Task,
    status_code=202,
)
async def create_smart_rubric_endpoint(
        job_id: UUID = Path(...),
        db_session: Session = Depends(get_db),
):
    """
    Queues rubric generation from the stored job description text.
    """
    try:
        file_wrapper = await retrieve_job_description_file(job_id, db_session)

        job_description_text = await asyncio.to_thread(
            extract_text_from_file,
            file_wrapper
        )

        async_result = celery_app.send_task(
            "tasks.create_rubric_task",
            args=[str(job_description_text)],
        )

        return Task(
            task_id=async_result.id,
            state=async_result.state,
            result=async_result.result,
        )

    except HTTPException:
        # Preserve explicit HTTP errors raised by underlying dependencies.
        raise
    except Exception:
        logger.exception("Error sending rubric task")
        raise HTTPException(
            status_code=500,
            detail="Error dispatching rubric task"
        )