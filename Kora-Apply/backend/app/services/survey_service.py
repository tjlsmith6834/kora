import os
import httpx
import logging
from uuid import UUID
from typing import Dict

logger = logging.getLogger(__name__)


def _get_applications_base_url() -> str:
    applications_base_url = os.getenv("APPLICATIONS_SERVICE_BASE_URL")
    if not applications_base_url:
        raise ValueError("APPLICATIONS_SERVICE_BASE_URL is not set")
    return applications_base_url


async def dispatch_survey_task(application_id: UUID) -> Dict:
    applications_base_url = _get_applications_base_url()
    url = f"{applications_base_url}/{application_id}/survey/"
    logger.info("Dispatching survey task for application_id=%s", application_id)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as http_err:
            logger.error("HTTP error dispatching survey task: %s", http_err)
            raise
        except Exception as err:
            logger.error("Unexpected error dispatching survey task: %s", err)
            raise

