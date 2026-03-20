import logging

from fastapi import APIRouter, HTTPException, Path

from common.models_schemas.schemas import Task
from common.celery_config import celery_app

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs/tasks",
    tags=["Tasks"],
)

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str = Path(..., description="The ID of the Celery task")
):
    """
    Returns current Celery task state and result when available.
    """
    try:
        logger.info(f"Fetching status for task_id={task_id}")
        async_result = celery_app.AsyncResult(task_id)

        # Build a normalized response from the Celery async result.
        task = Task(
            task_id=task_id,
            state=async_result.state,
            result=async_result.result
        )

        # Preserve existing behavior: failed background tasks return HTTP 500.
        if task.state == "FAILURE":
            logger.error(f"Task failed, task_id={task_id}, info={async_result.info}")
            raise HTTPException(status_code=500, detail="Task failed")

        return task
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Error retrieving task, task_id={task_id}")
        raise HTTPException(status_code=500, detail="Error retrieving task")