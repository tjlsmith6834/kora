import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Body, Path, Header
from typing import Optional
from uuid import UUID
from ..services import create_new_application, complete_application, submit_question_answer_gateway
from ..services.application_service import store_form_question_answer
from ..services.auth import authenticate_job_id_and_public_key
from ..schemas import NewApplication, QAResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/applications",
    tags=["New Application"],
)

@router.post("/")
async def submit_application(
        public_key: str = Header(..., alias="X-Public-Key"),
        job_id: UUID = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        candidate_email: str = Form(...),
        resume: UploadFile = File(...),
        linkedin_url: Optional[str] = Form(None),
        portfolio_url: Optional[str] = Form(None),
        github_url: Optional[str] = Form(None),
):
    try:
        logger.info(f"Submitting application for job: {job_id}")
        is_valid = await authenticate_job_id_and_public_key(job_id, public_key.encode())
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid public key for organization")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error during public key validation")
        raise HTTPException(status_code=500, detail="Internal auth error")

    application_data = NewApplication(
        job_id = job_id,
        first_name = first_name,
        last_name = last_name,
        email = candidate_email,
        linkedin_url = linkedin_url,
        portfolio_url = portfolio_url,
        github_url = github_url,
    )

    try:
        application_response = await create_new_application(application_data, resume)
        return {"application_id": application_response["application_id"]}
    except Exception:
        logger.exception("Failed to process submit_application request")
        raise HTTPException(status_code=500, detail="Failed to process request")

@router.post("/{application_id}/form_question_answers/")
async def save_form_answer_endpoint(
        public_key: str = Header(..., alias="X-Public-Key"),
        job_id: UUID = Header(..., alias="X-Job-ID"),
        application_id: UUID = Path(..., description="The application ID for which the answer is being stored"),
        qa_response: QAResponse = Body(...)
):
    logger.info("Running save_form_question_answer")
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
        logger.info(
            f"Running save_answer_endpoint for application {application_id}\n"
            f"Question: {qa_response.question}, Answer: {qa_response.answer}"
        )

        qa_id = await store_form_question_answer(application_id, qa_response)

        return {
            "message": "Question answer stored successfully",
            "qa_id": qa_id,
        }
    except Exception:
        logger.exception("Error storing form question answer")
        raise HTTPException(status_code=500, detail="Error storing question answer")

@router.post("/{application_id}/question_answers/")
async def save_answer_endpoint(
        public_key: str = Header(..., alias="X-Public-Key"),
        job_id: UUID = Header(..., alias="X-Job-ID"),
        application_id: UUID = Path(..., description="The application ID for which the answer is being stored"),
        qa_response: QAResponse = Body(...)
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
        logger.info(
            f"Running save_answer_endpoint for application {application_id}\n"
            f"Question: {qa_response.question}, Answer: {qa_response.answer}"
        )

        qa_id = await submit_question_answer_gateway(application_id, qa_response)

        return {
            "message": "Question answer stored successfully",
            "qa_id": qa_id,
        }
    except Exception:
        logger.exception("Error storing question answer")
        raise HTTPException(status_code=500, detail="Error storing question answer")

@router.post("/{application_id}/complete")
async def post_complete_application(
        public_key: str = Header(..., alias="X-Public-Key"),
        job_id: UUID = Header(..., alias="X-Job-ID"),
        application_id: UUID = Path(...)
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
        logger.info(f"Completing application: {application_id}")
        application_id = await complete_application(application_id)
        return {
            "message": "Application completed successfully",
            "application_id": application_id,
        }
    except Exception:
        logger.exception("Failed to complete application")
        raise HTTPException(status_code=500, detail="Failed to complete application")