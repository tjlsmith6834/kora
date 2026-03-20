import asyncio
from uuid import UUID
import logging

from ..services.embedding_services import generate_qa_embedding_for_entry
from common.celery_config import celery_app
from common.storage_retrieval_services import SessionLocal


@celery_app.task(name="tasks.generate_qa_embedding_task", bind=True, ignore_result=True)
def generate_survey_task(self, qa_id: UUID):
    """
    Celery task to create survey asynchronously.
    """
    logging.info(f"Running celery task generate_qa_embedding_task for application_id: {qa_id}")

    db_session = SessionLocal()

    try:
        record_id = asyncio.run(generate_qa_embedding_for_entry(qa_id, db_session))
        logging.info(f"Celery task stored embedding at id: {record_id}")

        return record_id

    except Exception as e:
        logging.error(f"Error creating embedding: {str(e)}")
        raise

    finally:
        db_session.close()