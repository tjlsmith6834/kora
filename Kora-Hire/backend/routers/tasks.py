import logging
from fastapi import APIRouter, HTTPException, Path, status, Depends
from uuid import UUID

from services.tasks import fetch_task_by_task_id
from services.auth import get_current_user_token
from schemas import Task
from schemas.auth import TokenPayload

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)

@router.get("/{task_id}", response_model=Task)
async def get_task_by_task_id(
        token: TokenPayload = Depends(get_current_user_token),
        task_id: UUID = Path(...),
):
    try:
        task_response: Task = await fetch_task_by_task_id(task_id)
        return task_response
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in get_task_by_task_id")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
