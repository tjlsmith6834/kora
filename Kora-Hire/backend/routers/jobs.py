from fastapi import APIRouter, Depends, HTTPException, status, Path, File, UploadFile, Body, Path
from uuid import UUID
from typing import Optional, List
import logging

from services.auth import get_current_user_token
from services.jobs import fetch_job_by_organization_id, store_job, fetch_job_by_job_id, store_job_rubric_by_job_id, fetch_job_rubric_by_job_id, store_job_description_by_job_id, retrieve_job_description_file_name_by_job_id, store_form_questions, retrieve_form_questions
from services.accounts import get_user
from schemas import JobList, Rubric, Job, SimpleResponse, RubricIn, JobFrame
from schemas.jobs import FormQuestionsIn, FormQuestionsOut
from schemas.auth import TokenPayload

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

@router.get("/", response_model=JobList)
async def get_jobs_for_user(
        token: TokenPayload = Depends(get_current_user_token)
):
    """
    Pull organization_id from the JWT claims and return that org's jobs.
    """
    user = await get_user(token.uid)
    logger.info(f"Getting jobs for user's org {user.org_id}")
    try:
        return await fetch_job_by_organization_id(user.org_id)
    except HTTPException:
        # if our service already raised an HTTPException,
        # just let FastAPI turn it into a response
        raise
    except Exception:
        logger.exception("Unexpected error in get_jobs_for_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=Job)
async def post_job(
        token: TokenPayload = Depends(get_current_user_token),
        new_job_data: JobFrame = Body(...),
):
    user = await get_user(token.uid)
    org_id = user.org_id

    try:
        stored_job = await store_job(new_job_data, org_id)
        logger.info(f"Stored job {stored_job}")
        return stored_job
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error posting job")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{job_id}", response_model=Job)
async def get_job_by_job_id(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
):
    try:
        rubric = await fetch_job_by_job_id(job_id)
        return rubric
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error getting job by id")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{job_id}/rubric", response_model=Rubric)
async def post_rubric_for_job(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
        rubric: RubricIn = Body(...)
):
    try:
        rubric = await store_job_rubric_by_job_id(job_id, rubric)
        return rubric
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error posting rubric")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{job_id}/rubric", response_model=Optional[Rubric])
async def get_rubric_for_job(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
):
    try:
        rubric: Optional[Rubric] = await fetch_job_rubric_by_job_id(job_id)
        return rubric
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error getting rubric")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{job_id}/description")
async def post_job_description(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
        description: UploadFile = File(...)
):
    try:
        file_url, file_name = await store_job_description_by_job_id(job_id, description)
        return {
            "file_url": file_url,
            "file_name": file_name,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error posting job description")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{job_id}/description/file_name", response_model=SimpleResponse)
async def get_job_description_file_name(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
):
    try:
        retrieved_file_name: str = await retrieve_job_description_file_name_by_job_id(job_id)
        return SimpleResponse(
            message="Successfully retrieved job description file name",
            content=retrieved_file_name,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error retrieving job description file name")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{job_id}/form_questions", response_model=FormQuestionsOut)
async def post_form_questions(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
        form_questions: FormQuestionsIn = Body(...),
):
    try:
        stored_questions: FormQuestionsOut = await store_form_questions(job_id, form_questions)
        return stored_questions
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error storing form questions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{job_id}/form_questions", response_model=FormQuestionsOut)
async def get_form_questions(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Path(...),
):
    try:
        stored_questions: FormQuestionsOut = await retrieve_form_questions(job_id)
        return stored_questions
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error retrieving form questions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
