from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Body, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
import logging
logger = logging.getLogger(__name__)

from api_worker.services.applications import (
    store_new_application_and_resume,
    complete_application,
    store_form_question_answer,
    retrieve_form_question_answer,
    hide_application
)
from api_worker.services.application_question_answers import (
    store_question_answer,
    retrieve_interview_question_answers
)
from api_worker.services.profiles import (
    get_profiles2_by_job_id,
    get_profile2_by_application_id
)

from common.celery_config import celery_app
from common.storage_retrieval_services.db import get_db
from common.storage_retrieval_services.retrieve_docs import retrieve_primary_resume
from common.models_schemas.schemas import NewApplication, QAResponse
from common.models_schemas.schemas.profiles import Profile2

router = APIRouter(
    prefix="/applications",
    tags=["Application"],
)

@router.post("/")
async def new_application_endpoint(
    job_id: UUID = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    linkedin_url: Optional[str] = Form(None),
    portfolio_url: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    try:
        # Validate and extract textual fields
        application_data = NewApplication(
            job_id=job_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            linkedin_url=linkedin_url,
            portfolio_url=portfolio_url,
            github_url=github_url,
        )
        # Pass the validated text and file(s) separately to the service
        new_application_id_resume = await store_new_application_and_resume(application_data, resume, db_session)
        return {
            "message": "Application stored successfully",
            "application_id": new_application_id_resume[0],
        }
    except Exception as e:
        logger.exception("Error storing application")
        raise HTTPException(status_code=500, detail="Error storing application")

@router.post("/{application_id}/form_question_answer")
async def post_form_question_answer(
        application_id: UUID = Path(...),
        qa_response: QAResponse = Body(...),
        db_session: Session = Depends(get_db)
):
    id = await store_form_question_answer(application_id, qa_response, db_session)
    return {
        "id": id,
    }

@router.get("/{application_id}/form_question_answer")
async def get_form_question_answer(
        application_id: UUID = Path(...),
        db_session: Session = Depends(get_db)
):
    question_answers = await retrieve_form_question_answer(application_id, db_session)
    return question_answers


@router.get("/profiles/", response_model=List[Profile2])
async def get_profiles_by_job_id_endpoint(
    job_id: UUID = Query(..., description="Get profiles by the UUID of the job"),
    db: Session = Depends(get_db)
) -> List[Profile2]:
    if job_id is not None:
        return get_profiles2_by_job_id(job_id, db)

@router.get("/{application_id}/profile/", response_model=Profile2)
async def get_profile_by_application_id_endpoint(
    application_id: UUID = Path(..., description="Get profiles by the UUID of the application"),
    db: Session = Depends(get_db)
) -> Profile2:
    return get_profile2_by_application_id(application_id, db)

@router.post("/{application_id}/survey/")
async def queue_survey_endpoint(
    application_id: UUID
):
    """
    Queues asynchronous survey generation for the provided application ID.
    """
    try:
        # Queue the survey generation task and return its tracking ID.
        logger.info("🔜 about to send survey task")
        task = celery_app.send_task("tasks.generate_survey_task", args=[str(application_id)])
        logger.info(f"🔚 send_task returned, id={task.id!r}")
        return {
            "message": "Survey generation task queued",
            "task_id": task.id,
            "application_id": application_id
        }

    except Exception as e:
        logger.exception("Error sending survey task")
        raise HTTPException(status_code=500, detail="Error sending survey task")

@router.post("/{application_id}/new_profile/")
async def queue_profile_endpoint(
    application_id: UUID
):
    """
    Queues asynchronous profile generation for the provided application ID.
    """
    try:
        # Queue the profile generation task and return its tracking ID.
        logger.info("🔜 about to send profile task")
        task = celery_app.send_task("tasks.generate_store_profile_task", args=[str(application_id)])
        logger.info(f"🔚 send_task returned, id={task.id!r}")
        return {
            "message": "Profile generation task queued",
            "task_id": task.id,
            "application_id": application_id
        }

    except Exception as e:
        logger.exception("Error sending profile task")
        raise HTTPException(status_code=500, detail="Error sending profile task")

@router.post("/{application_id}/question_answer/")
async def question_answer_endpoint(
    application_id: UUID,
    qa_response: QAResponse = Body(...),
    db_session: Session = Depends(get_db)
):
    try:

        logger.info(
            f"Running store_question_answer for application {application_id}\n"
            f"Question: {qa_response.question}, Answer: {qa_response.answer}"
        )

        # Await the async service call, passing the DB session as well.
        qa_id = await store_question_answer(application_id, qa_response, db_session)
        task = celery_app.send_task("tasks.generate_qa_embedding_task", args=[str(qa_id)])

        return {
            "message": "Question answer stored successfully",
            "qa_id": qa_id,
        }

    except Exception as e:
        logger.exception("Error storing question answer")
        raise HTTPException(status_code=500, detail="Error storing question answer")

@router.get("/{application_id}/interview_question_answers")
async def get_interview_question_answers(
        application_id: UUID = Path(...),
        db_session: Session = Depends(get_db)
):
    question_answers = await retrieve_interview_question_answers(application_id, db_session)
    return question_answers

@router.get(
    "/{application_id}/resume/",
    summary="Download the primary resume for an application",
    response_class=StreamingResponse,
)
async def primary_resume_endpoint(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Streams back the single document marked `is_primaryresume=True` for the given application.
    """
    file_wrapper = await retrieve_primary_resume(application_id, db)
    if not file_wrapper:
        raise HTTPException(status_code=404, detail="Primary resume not found")

    return StreamingResponse(
        file_wrapper.file,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{file_wrapper.name}"'}
    )

@router.post(
    "/{application_id}/complete/",
)
async def post_application_complete_endpoint(
    application_id: UUID = Path(...),
    db: Session = Depends(get_db),
):
    try:
        logger.info(f"Running post_application_complete for application {application_id}")
        response = await complete_application(application_id)
        logger.info(
            f'Completed application {response.get("application_id")}\n'
            f'Analysis task_id: {response.get("task_id")}'
        )
        return response
    except Exception as e:
        logger.exception("Error running post_application_complete")
        raise HTTPException(status_code=500, detail="Error running post_application_complete")


@router.post("/{qa_id}/analyze/")
async def analyze_question_answer_endpoint(
    qa_id: UUID = Path(...),
):
    """
    Queues QA embedding analysis for a stored question-answer record.
    """
    try:
        # Queue the embedding task and return its tracking ID.
        task = celery_app.send_task("tasks.generate_qa_embedding_task", args=[str(qa_id)])
        return {
            "message": "QA analysis task queued",
            "task_id": task.id,
            "qa_id": qa_id,
        }

    except Exception as e:
        logger.exception("Error sending QA analysis task")
        raise HTTPException(status_code=500, detail="Error sending QA analysis task")

@router.put(
    "/{application_id}/hide/",
)
async def post_application_hide_endpoint(
    application_id: UUID = Path(...),
    db: Session = Depends(get_db),
):
    try:
        logger.info(f"Running post_application_hide for application {application_id}")
        await hide_application(application_id, db)
        logger.info(
            f"Hid application {application_id}"
        )
        return {"message": "Application hidden", "application_id": application_id}
    except Exception as e:
        logger.exception("Error running post_application_hide")
        raise HTTPException(status_code=500, detail="Error running post_application_hide")

@router.post("/{application_id}/career_test/")
async def queue_career_test_endpoint(
    application_id: UUID = Path(...),
):
    """
    Queues career inference for the provided application ID.
    """
    try:
        # Queue the career task and return its tracking ID.
        task = celery_app.send_task("tasks.find_career", args=[str(application_id)])
        return {
            "message": "Career task queued",
            "task_id": task.id,
            "application_id": application_id,
        }

    except Exception as e:
        logger.exception("Error sending career task")
        raise HTTPException(status_code=500, detail="Error sending career task")



