import logging
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.models_schemas.schemas import QAResponse
from common.models_schemas.models import ApplicationQuestionsAnswers

logger = logging.getLogger(__name__)


async def store_question_answer(application_id: UUID, response: QAResponse, db: Session) -> UUID:
    """Saves an answer for a given application."""

    logger.info(
        "store_question_answer application_id=%s question=%r",
        application_id,
        response.question,
    )

    question_answer = ApplicationQuestionsAnswers(
        application_id=application_id,
        question_text=response.question,
        answer_text=response.answer,
    )

    try:
        db.add(question_answer)
        db.commit()
        db.refresh(question_answer)
    except Exception:
        db.rollback()
        raise

    qa_id = question_answer.qa_id
    logger.info("Saved question_answer qa_id=%s application_id=%s", qa_id, application_id)
    return qa_id


async def retrieve_interview_question_answers(application_id: UUID, db_session: Session) -> List[QAResponse]:
    stmt = (
        select(
            ApplicationQuestionsAnswers.question_text,
            ApplicationQuestionsAnswers.answer_text,
        )
        .select_from(ApplicationQuestionsAnswers)
        .where(ApplicationQuestionsAnswers.application_id == application_id)
        .order_by(ApplicationQuestionsAnswers.qa_id)
    )

    results = db_session.execute(stmt).all()
    return [
        QAResponse(question=question, answer=answer)
        for question, answer in results
    ]
