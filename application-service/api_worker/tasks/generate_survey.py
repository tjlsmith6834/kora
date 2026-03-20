import asyncio
from uuid import UUID
import logging

from ..services.application_analysis_services.analyze_application import analyze_application
from ..services.embedding_services import generate_application_faiss_index
from ..services.survey_services import write_open_questions2, write_open_questions3
from ..utils.retrieve_rubrics import get_application_rubric_context
from ..utils.text_from_file_utils import extract_text_from_file

from common.celery_config import celery_app
from common.storage_retrieval_services import SessionLocal, retrieve_primary_resume


@celery_app.task(name="tasks.generate_survey_task", bind=True, ignore_result=False)
def generate_survey_task(self, application_id: UUID):
    """
    Celery task to create survey asynchronously.
    """
    logging.info(f"Running celery task generate_survey_task for application_id: {application_id}")

    db_session = SessionLocal()

    try:
        async def async_generate_survey(application_id, db_session):
            index, metadata = await generate_application_faiss_index(application_id, db_session)
            job_id, rubric, focus_embeddings, criteria_embeddings =  await get_application_rubric_context(application_id, db_session)
            application_analysis = await analyze_application(index, metadata, application_id, db_session, rubric, focus_embeddings, criteria_embeddings)
            survey = await write_open_questions2(application_analysis, rubric)

            return survey

        async def async_generate_survey_2(application_id, db_session):
            application_file = await retrieve_primary_resume(application_id, db_session)
            application_text = extract_text_from_file(application_file)
            job_id, rubric, focus_embeddings, criteria_embeddings = await get_application_rubric_context(application_id,
                                                                                                         db_session)
            survey2 = await write_open_questions2(application_text, rubric)

            return survey2



        """survey_response = asyncio.run(async_generate_survey(application_id, db_session))"""
        survey_response = asyncio.run(async_generate_survey_2(application_id, db_session))
        logging.info(f"Celery task created survey: {survey_response}")

        return survey_response.model_dump()

    except Exception as e:
        logging.error(f"Error creating survey: {str(e)}")
        raise

    finally:
        db_session.close()

