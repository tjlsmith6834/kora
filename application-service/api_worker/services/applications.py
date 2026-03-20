import logging
from datetime import datetime
from typing import Dict, List, Tuple
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .application_docs import store_uploaded_files

from common.celery_config import celery_app
from common.models_schemas.models import Application
from common.models_schemas.models.application import FormQuestionAnswers
from common.models_schemas.schemas import NewApplication, QAResponse

logger = logging.getLogger(__name__)


async def store_new_application_and_resume(
    application_data: NewApplication,
    resume: UploadFile,
    db: Session,
) -> Tuple[UUID, List[str]]:
    new_application_id = await store_new_application(application_data, db)
    doc_urls = await store_uploaded_files(new_application_id, [resume], db, True)
    return new_application_id, doc_urls


async def store_new_application(application_data: NewApplication, db: Session) -> UUID:
    """Handles application creation."""
    application = Application(
        job_id=application_data.job_id,
        candidate_first_name=application_data.first_name,
        candidate_last_name=application_data.last_name,
        candidate_email=application_data.email,
        linkedin=application_data.linkedin_url,
        portfolio=application_data.portfolio_url,
        github=application_data.github_url,
        application_status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    try:
        db.add(application)
        db.commit()
        db.refresh(application)
    except Exception:
        db.rollback()
        raise

    if isinstance(application.application_id, set):
        application_id = next(iter(application.application_id))
    else:
        application_id = application.application_id

    return application_id


async def store_form_question_answer(
    application_id: UUID, response: QAResponse, db: Session
) -> UUID:
    """Persist one form question answer for an application."""
    form_question_answer = FormQuestionAnswers(
        application_id=application_id,
        question=response.question,
        answer=response.answer,
    )
    try:
        db.add(form_question_answer)
        db.commit()
        db.refresh(form_question_answer)
    except Exception:
        db.rollback()
        raise

    row_id = form_question_answer.id
    logger.info("Saved form question answer id=%s application_id=%s", row_id, application_id)
    return row_id


async def retrieve_form_question_answer(
    application_id: UUID, db_session: Session
) -> List[QAResponse]:
    """Return all stored form Q&A rows for an application."""
    stmt = (
        select(FormQuestionAnswers.question, FormQuestionAnswers.answer)
        .select_from(FormQuestionAnswers)
        .where(FormQuestionAnswers.application_id == application_id)
        .order_by(FormQuestionAnswers.id)
    )
    results = db_session.execute(stmt).all()
    return [QAResponse(question=q, answer=a) for q, a in results]


async def complete_application(application_id: UUID) -> Dict:
    logger.info("Completing application: %s", application_id)
    task = celery_app.send_task(
        "tasks.generate_store_profile_task", args=[str(application_id)]
    )
    return {"task_id": task.id, "application_id": application_id}


async def hide_application(application_id: UUID, db: Session) -> UUID:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application.application_status = "hidden"
    application.analysis_task_id = None
    db.add(application)
    db.commit()

    return application_id
