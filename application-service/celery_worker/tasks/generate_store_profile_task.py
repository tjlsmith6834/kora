import asyncio
import logging
from uuid import UUID

from ..services.profile_services.career_path_service import extract_and_store_career_path
from ..services.profile_services.create_profile_scores import create_profile_scores
from ..services.profile_services.create_profile_bullets import generate_profile_bullets
from ..services.profile_services.create_profile_recent_roles import find_extract_recent_roles
from ..services.db_services.store_candidate_profile import store_candidate_profile
from ..services.db_services.store_recent_roles import store_recent_roles_for_application

from common.celery_config import celery_app
from common.storage_retrieval_services import SessionLocal

@celery_app.task(name="tasks.generate_store_profile_task", bind=True, ignore_result=True)
def generate_store_profile_task(self, application_id: UUID):
    logging.info(f"Running celery task generate_store_profile_task for application_id: {application_id}")
    db_session = SessionLocal()

    async def process_application(application_id, db_session):
        results = await asyncio.gather(
            extract_and_store_career_path(application_id, db_session),
            create_profile_scores(application_id, db_session),
        )
        return results

    try:
        recent_roles = asyncio.run(find_extract_recent_roles(application_id, db_session))
        store_recent_roles_for_application(application_id, recent_roles, db_session)

        career_path, (profile_rubric, profile_score) = asyncio.run(
            process_application(application_id, db_session)
        )

        profile_bullets = asyncio.run(generate_profile_bullets(profile_rubric))


        logging.info(f"Extracted career: {career_path}")
        logging.info(f"Extracted profile rubric: {profile_rubric}")
        logging.info(f"Extracted profile score: {profile_score}")
        logging.info(f"Extracted bullets: {profile_bullets}")

        asyncio.run(store_candidate_profile(application_id, profile_score, profile_rubric, profile_bullets, career_path, db_session))

        return application_id

    except Exception as e:
        logging.error(f"Error creating profile: {str(e)}")
        raise

    finally:
        db_session.close()