from typing import Optional, List

from fastapi import APIRouter, Depends, Body, Path, Query, File, UploadFile
from fastapi import HTTPException

from sqlalchemy.orm import Session
from uuid import UUID
import logging

from ..services.jobs import store_job, retrieve_job, fetch_jobs_by_organization_id, store_form_questions, fetch_form_questions, store_link_config, fetch_link_config
from ..services.job_descriptions import store_job_description, retrieve_job_description_file_name
from ..services.rubrics import fetch_rubric_by_job_id, store_rubric, retrieve_rubric_category_embeddings_by_job_id

from common.models_schemas.schemas import JobIn, JobOut, JobOutList, RubricOut, RubricIn, SimpleResponse, RubricCategoryEmbeddingsOut
from common.models_schemas.schemas.jobs import FormQuestionsIn, FormQuestionsOut, LinkConfig
from common.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

@router.post("/", response_model=JobOut, status_code=201)
async def post_jobs(
        job_data: JobIn = Body(...),
        db_session: Session = Depends(get_db)
):
    try:
        stored_job = await store_job(job_data, db_session)
        return stored_job
    except Exception:
        logger.exception("Error storing job")
        raise HTTPException(status_code=500, detail="Error storing job")

@router.get("/", response_model=JobOutList)
async def get_jobs(
        organization_id: UUID = Query(..., description="The user with access to jobs"),
        db_session: Session = Depends(get_db)
):
    try:
        job_list: JobOutList = await fetch_jobs_by_organization_id(organization_id, db_session)
        return job_list
    except Exception:
        logger.exception("Error getting jobs")
        raise HTTPException(status_code=500, detail="Error getting jobs")

@router.get("/{job_id}", response_model=JobOut)
async def get_job_by_job_id(
        job_id: UUID = Path(...),
        db_session: Session = Depends(get_db)
):
    try:
        job: JobOut = await retrieve_job(job_id, db_session)
        return job
    except Exception:
        logger.exception("Error getting job")
        raise HTTPException(status_code=500, detail="Error getting job")

@router.post("/{job_id}/description")
async def post_job_description(
        job_id: UUID = Path(...),
        job_description_file: UploadFile = File(...),
        db_session: Session = Depends(get_db)
):
    try:
        file_url, file_name = await store_job_description(job_id, job_description_file, db_session)
        return {
                "message": "Job description stored",
                "file_url": file_url,
                "file_name": file_name
        }
    except Exception:
        logger.exception("Error storing job description")
        raise HTTPException(status_code=500, detail="Error storing job description")

@router.get("/{job_id}/description/file_name", response_model=SimpleResponse)
async def get_job_description_file_name(
        job_id: UUID = Path(...),
        db_session: Session = Depends(get_db)
):
    try:
        file_name: str = await retrieve_job_description_file_name(job_id, db_session)
        return SimpleResponse(
            message="Found job description",
            content=file_name,
        )
    except Exception:
        logger.exception("Error getting job description file name")
        raise HTTPException(status_code=500, detail="Error getting job description file name")

@router.post("/{job_id}/rubric", response_model=RubricOut)
async def post_rubric(
        rubric: RubricIn,
        job_id: UUID = Path(...),
        db_session: Session = Depends(get_db)
):
    try:
        saved_rubric: RubricOut = await store_rubric(rubric, job_id, db_session)
        return saved_rubric
    except Exception:
        logger.exception("Error storing rubric")
        raise HTTPException(status_code=500, detail="Error storing rubric")

@router.get("/{job_id}/rubric", response_model=Optional[RubricOut])
async def get_rubric_by_job_id(
        job_id: UUID,
        db_session: Session = Depends(get_db)
):
    try:
        rubric: Optional[RubricOut] = await fetch_rubric_by_job_id(job_id, db_session)
        return rubric
    except Exception:
        logger.exception("Error fetching rubric")
        raise HTTPException(status_code=500, detail="Error fetching rubric")

@router.get("/{job_id}/rubric/embeddings", response_model=List[RubricCategoryEmbeddingsOut])
async def get_rubric_embeddings_by_job_id(
        job_id: UUID,
        db_session: Session = Depends(get_db)
):
    try:
        rubric: List[RubricCategoryEmbeddingsOut] = await retrieve_rubric_category_embeddings_by_job_id(job_id, db_session)
        return rubric
    except Exception:
        logger.exception("Error fetching rubric embeddings")
        raise HTTPException(status_code=500, detail="Error fetching rubric embeddings")


@router.post("/{job_id}/form_questions", response_model=FormQuestionsOut)
async def post_form_questions(
        job_id: UUID = Path(...),
        form_questions: FormQuestionsIn = Body(...),
        db_session: Session = Depends(get_db)
):
    try:
        stored_questions: FormQuestionsOut = await store_form_questions(job_id, form_questions, db_session)
        return stored_questions
    except Exception:
        logger.exception("Error storing form questions")
        raise HTTPException(status_code=500, detail="Error storing form questions")

@router.get("/{job_id}/form_questions", response_model=FormQuestionsOut)
async def get_form_questions(
        job_id: UUID = Path(...),
        db_session: Session = Depends(get_db)
):
    try:
        questions: FormQuestionsOut = await fetch_form_questions(job_id, db_session)
        return questions
    except Exception:
        logger.exception("Error fetching form questions")
        raise HTTPException(status_code=500, detail="Error fetching form questions")

@router.post("/{job_id}/link_config", response_model=None)
async def post_link_config(
        job_id: UUID = Path(...),
        config: LinkConfig = Body(...),
        db_session: Session = Depends(get_db)
):
    try:
        await store_link_config(job_id, config, db_session)
    except Exception:
        logger.exception("Error storing link config")
        raise HTTPException(status_code=500, detail="Error storing link config")

@router.get("/{job_id}/link_config", response_model=LinkConfig)
async def get_link_config(
        job_id: UUID = Path(...),
        db_session: Session = Depends(get_db)
):
    try:
        config: LinkConfig = await fetch_link_config(job_id, db_session)
        return config
    except Exception:
        logger.exception("Error fetching link config")
        raise HTTPException(status_code=500, detail="Error fetching link config")


