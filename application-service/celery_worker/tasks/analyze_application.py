import asyncio
import logging
from uuid import UUID

from ..services.embedding_services import generate_application_faiss_index
from celery_worker.services.db_services.store_candidate_profile import store_candidate_profile

from common.celery_config import celery_app
from common.models_schemas.models import Application
from common.storage_retrieval_services import SessionLocal

@celery_app.task(name="tasks.analyze_application_task", bind=True, ignore_result=True)
def analyze_application_task(self, application_id: UUID):
    """
    Celery task to process application analysis asynchronously.
    """
    db = SessionLocal()
    try:
        task_id = UUID(self.request.id)
        logging.info(f"Celery Task: Analyzing application {application_id}")

        application_db = db.query(Application).get(application_id)
        if not application_db or application_db.analysis_task_id != task_id:
            # It was deleted or updated → abort immediately, no work done
            logging.info(
                f"Aborting build_store_rubric_embeddings_task due to stale task_id\n"
                f"Current task_id: {task_id}\n"
                f"Most recent stored task_id: {application_db.analysis_task_id}"
            )
            return

        # Generate FAISS index
        index, metadata = asyncio.run(generate_application_faiss_index(application_id, db))

        # Run profile analysis
        application_analysis = asyncio.run(
            analyze_application(index, metadata, application_id, db)
        )

        # Store the analysis result
        application_db = db.query(Application).filter(Application.application_id == application_id).one_or_none()
        if not application_db or application_db.analysis_task_id != task_id:
            # It was deleted or updated → Do not store analysis results
            logging.info(
                f"Aborting store_candidate_profile due to stale task_id\n"
                f"Current task_id: {task_id}\n"
                f"Most recent stored task_id: {application_db.analysis_task_id}"
            )
            return


        asyncio.run(store_candidate_profile(application_analysis, db))

        logging.info(f"Successfully stored analysis for application {application_id}")

    except Exception as e:
        logging.error(f"❌ Error in analyze_application_task: {str(e)}")
        raise

    finally:
        db.close()