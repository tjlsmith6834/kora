from fastapi import APIRouter, HTTPException, Query, Header
from uuid import UUID
from ..services import dispatch_survey_task
from ..services.auth import authenticate_job_id_and_public_key
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/surveys",
    tags=["Survey"],
)

@router.post("/")
async def queue_survey(
        public_key: str = Header(..., alias="X-Public-Key"),
        job_id: UUID = Header(..., alias="X-Job-ID"),
        application_id: UUID = Query(..., description="The application ID used to generate the survey"),
):
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
        # Queue survey generation and return a task ID for polling.
        task_data = await dispatch_survey_task(application_id)

        task_id = task_data.get("task_id")
        if not task_id:
            raise HTTPException(status_code=500, detail="No task id returned from dispatch.")

        return {"task_id": task_id}

    except Exception:
        logger.exception("Error generating survey")
        raise HTTPException(status_code=500, detail="Error calling AI Gateway")