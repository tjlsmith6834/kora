import os
import httpx
from fastapi import HTTPException
from uuid import UUID
import logging

from schemas import Task

logger = logging.getLogger(__name__)

jobs_service_tasks_url = os.getenv("JOBS_SERVICE_TASKS_URL")
if not jobs_service_tasks_url:
    raise ValueError("JOBS_SERVICE_TASKS_URL is not set")

async def fetch_task_by_task_id(task_id: UUID) -> Task:
    url = f"{jobs_service_tasks_url}/{task_id}"
    logger.info(f"Fetching task from gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logger.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail="Jobs service error")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logger.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        task_raw = resp.json()
    except ValueError:
        logger.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")
    try:
        # Build our Pydantic models
        return Task(**task_raw)
    except Exception as exc:
        logger.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")