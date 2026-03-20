import asyncio
import logging
from uuid import UUID

from celery_worker.services.profile_services.create_profile_recent_roles import find_extract_recent_roles
from celery_worker.services.db_services.store_recent_roles import store_recent_roles_for_application

from common.celery_config import celery_app
from common.storage_retrieval_services import SessionLocal

@celery_app.task(name="tasks.find_career", bind=True, ignore_result=True)
def find_career(self, application_id: UUID):
    """
    Celery task to process application analysis asynchronously.
    """
    db = SessionLocal()
    try:
        task_id = UUID(self.request.id)
        logging.info(f"Celery Task: Analyzing application {application_id}")

        # Run profile analysis
        recent_roles = asyncio.run(
            find_extract_recent_roles(application_id, db)
        )

        logging.info(f"Roles extracted: \n{recent_roles}")

        store_recent_roles_for_application(application_id, recent_roles, db)

    except Exception as e:
        logging.error(f"❌ Error in find_career_task: {str(e)}")
        raise

    finally:
        db.close()