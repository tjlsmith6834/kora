from fastapi import APIRouter, HTTPException, Query, Header
from uuid import UUID

from ..services import poll_task_status
from ..services.auth import authenticate_job_id_and_public_key
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",  # New prefix with path parameter
    tags=["Survey"],
)

@router.get("/")
async def get_task_status(
        public_key: str = Header(..., alias="X-Public-Key"),
        job_id: UUID = Header(..., alias="X-Job-ID"),
        task_id: str = Query(..., description="The task primary identifier"),
):
    """
    Polls task status for a queued async job.
    """
    try:
        is_valid = await authenticate_job_id_and_public_key(job_id, public_key.encode())
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid public key for organization")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error during public key validation")
        raise HTTPException(status_code=500, detail="Internal auth error")

    try:
        poll_result = await poll_task_status(task_id)
        logger.info(f"Returning task: {poll_result}")
        return poll_result

    except Exception:
        logger.exception("Error polling task status")
        raise HTTPException(status_code=500, detail="Error calling AI Gateway")