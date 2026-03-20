import logging
from uuid import UUID

from common.db import SessionLocal

from ..services.create_store_rubric_category_embeddings import create_store_rubric_category_embeddings
from ..services.fetch_rubric_by_rubric_id import fetch_rubric_by_rubric_id

from common.celery_config import celery_app

@celery_app.task(name="tasks.create_store_rubric_embeddings_task")
def create_store_rubric_embeddings_task(rubric_id: str, task_id: str):
    """
    Celery task to process application analysis asynchronously.
    """
    try:
        db = SessionLocal()
        try:
            logging.info(
                f"Running build_store_rubric_embeddings_task\n" 
                f"Rubric_id: {rubric_id}\n"
                f"task_id: {task_id}"
            )
            tid = UUID(task_id)
            rubric = fetch_rubric_by_rubric_id(UUID(rubric_id), db)
            if not rubric or rubric.analysis_task_id != tid:
                # It was deleted or updated → abort immediately, no work done
                logging.info(
                    f"Aborting build_store_rubric_embeddings_task due to stale task_id\n"
                    f"Current task_id: {tid}\n"
                    f"Most recent stored task_id: {rubric.analysis_task_id}"
                )
                return

            rubric_embeddings = create_store_rubric_category_embeddings(rubric, db)
            payload = [r.model_dump() for r in rubric_embeddings]
            logging.info(f"Successfully created rubric embeddings: {tid}")
            return payload

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    except Exception as e:
        logging.error(f"Error creating rubric: {str(e)}")