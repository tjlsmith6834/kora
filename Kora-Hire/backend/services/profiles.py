import os
import httpx
from typing import List
from uuid import UUID
import logging

from schemas.profiles import Profile

logger = logging.getLogger(__name__)

application_service_base_url = os.getenv("APPLICATIONS_SERVICE_BASE_URL")
if not application_service_base_url:
    raise ValueError("APPLICATIONS_SERVICE_BASE_URL is not set")

TIMEOUT = httpx.Timeout(connect=5.0, read=35.0, write=10.0, pool=5.0)
LIMITS = httpx.Limits(max_keepalive_connections=10, max_connections=50)

async def fetch_profiles_by_job_id(job_id: UUID) -> List[Profile]:
    """
    Fetch all candidate profiles for a given job_id from the FastAPI gateway,
    and return them as a list of Pydantic Profile objects.
    """
    url = f"{application_service_base_url}/profiles/?job_id={job_id}"
    logger.info(f"Fetching profiles by job_id from gateway: {url}")

    async with httpx.AsyncClient(timeout=TIMEOUT, limits=LIMITS) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            response_json = response.json()
            logger.info("Fetched %s profiles for job_id=%s", len(response_json), job_id)

            profile_list = [Profile(**profile_json) for profile_json in response_json]

            return profile_list

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise

async def fetch_profile_by_application_id(application_id: UUID) -> Profile:
    """
    Fetch a candidate profile for a given application_id from the API gateway.
    """
    url = f"{application_service_base_url}/{application_id}/profile/"
    logger.info(f"Fetching profile by application_id from gateway: {url}")

    async with httpx.AsyncClient(timeout=TIMEOUT, limits=LIMITS) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            response_json = response.json()
            logger.info("Fetched profile for application_id=%s", application_id)

            profile = Profile(**response_json)

            return profile

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise