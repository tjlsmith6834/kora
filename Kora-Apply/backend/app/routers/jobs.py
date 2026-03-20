from fastapi import APIRouter, HTTPException, Path
from uuid import UUID
import logging

from ..services.jobs import retrieve_form_questions, retrieve_link_config
from ..schemas import FormQuestionList, LinkConfig

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

@router.get("/{job_id}/form_questions", response_model=FormQuestionList)
async def get_form_questions(
        job_id: UUID = Path(...),
):
    logger.info(f"Get form questions hit for job_id: {job_id}")
    try:
        response = await retrieve_form_questions(job_id)
        logger.info(f"Get form questions returning to FE: {response.model_dump()}")

        return response
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error retrieving form questions")
        raise HTTPException(status_code=500, detail="Error retrieving form questions")

@router.get("/{job_id}/link_config", response_model=LinkConfig)
async def get_link_config(
        job_id: UUID = Path(...),
):
    logger.info(f"Get link config hit for job_id: {job_id}")
    try:
        response = await retrieve_link_config(job_id)
        logger.info(f"Get link config returning to FE: {response.model_dump()}")
        return response
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error retrieving link config")
        raise HTTPException(status_code=500, detail="Error retrieving link config")