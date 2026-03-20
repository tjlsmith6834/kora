import logging

from fastapi import APIRouter, HTTPException, Path

from common.celery_config import celery_app

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/applications/tasks",
    tags=["Tasks"],
)

@router.get("/{task_id}")
async def get_task_status(
        task_id: str = Path(..., description="The ID of the Celery task")
):
    """
    Returns current Celery task state and result when available.
    """
    try:
        logger.info(f"Running get_task_status, task_id={task_id}")
        task_result = celery_app.AsyncResult(task_id)
        logger.info(f"Task state: {task_result.state}")
        if task_result.state == "PENDING" or task_result.state == "STARTED":
            return {"state": task_result.state, "result": None}
        elif task_result.state == "FAILURE":
            logger.error(f"Task failed, task_id={task_id}, info={task_result.info}")
            raise HTTPException(status_code=500, detail="Task failed")
        elif task_result.state == "SUCCESS":
            return {"state": task_result.state, "result": task_result.result}
        else:
            return {"state": task_result.state, "result": None}
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Error retrieving task status, task_id={task_id}")
        raise HTTPException(status_code=500, detail="Error retrieving task status")