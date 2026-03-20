import logging
import asyncio
from typing import Optional

from ..services.create_rubric_service import create_rubric

from common.celery_config import celery_app

@celery_app.task(name="tasks.create_rubric_task", bind=False)
def create_rubric_task(job_description: str, hiring_manager_voiceover: Optional[str] = None):
    """
    Celery task to process application analysis asynchronously.
    """
    try:
        logging.info(f"Celery Task: Create Rubric")

        rubric = asyncio.run(create_rubric(job_description, hiring_manager_voiceover))

        logging.info(f"Successfully created rubric: {rubric}")

        return rubric.model_dump()

    except Exception as e:
        logging.error(f"Error creating rubric: {str(e)}")