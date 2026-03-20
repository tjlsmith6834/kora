import os
import httpx
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def _get_applications_base_url() -> str:
    applications_base_url = os.getenv("APPLICATIONS_SERVICE_BASE_URL")
    if not applications_base_url:
        raise ValueError("APPLICATIONS_SERVICE_BASE_URL is not set")
    return applications_base_url


async def poll_task_status(task_id: str) -> Dict:
    logger.info(f"Running poll_task_status, task_id={task_id}")
    applications_base_url = _get_applications_base_url()
    url = f"{applications_base_url}/tasks/{task_id}"
    logger.info(f"Calling URL: {url}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("state") == "FAILURE":
                failure_detail = data.get("error") or data.get("result")
                raise Exception(f"Task failed: {failure_detail}")
            logger.info(f"Task found: {data}")
            return data
        except httpx.HTTPError as http_err:
            logger.error("HTTP error polling task status: %s", http_err)
            raise
        except Exception as err:
            logger.error("Error polling task status: %s", err)
            raise