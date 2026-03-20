from fastapi import APIRouter, HTTPException, Path, Depends
from uuid import UUID
import logging

from services.smart_rubrics import request_smart_rubric_by_job_id
from services.auth import get_current_user_token
from schemas import Task
from schemas.auth import TokenPayload

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/smart_rubrics",
    tags=["Smart Rubrics"],
)

@router.post("/{job_id}", response_model=Task)
async def create_smart_rubric_endpoint(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
):
    """
    Queues smart rubric generation for the provided job ID.
    """
    try:
        queued_task: Task = await request_smart_rubric_by_job_id(job_id)
        return queued_task

    except Exception:
        logger.exception("Error sending rubric task")
        raise HTTPException(status_code=500, detail="Error sending rubric task")