import os
import httpx
import logging
from fastapi import UploadFile
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from uuid import UUID

from ..schemas import NewApplication, QAResponse

logger = logging.getLogger(__name__)


def _get_applications_base_url() -> str:
    applications_base_url = os.getenv("APPLICATIONS_SERVICE_BASE_URL")
    if not applications_base_url:
        raise ValueError("APPLICATIONS_SERVICE_BASE_URL is not set")
    return applications_base_url


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
)
async def create_new_application(
    application_data: NewApplication,
    resume: UploadFile
) -> dict:
    """
    Calls Applications API to store a new application.
    """
    applications_base_url = _get_applications_base_url()
    url = f"{applications_base_url}/"
    logger.info("Creating new application via %s", url)

    # Create a dictionary for text fields. Convert UUID to string.
    data = {
        "job_id": str(application_data.job_id),
        "first_name": application_data.first_name,
        "last_name": application_data.last_name,
        "email": application_data.email,
    }

    if application_data.linkedin_url:
        data["linkedin_url"] = application_data.linkedin_url
    if application_data.portfolio_url:
        data["portfolio_url"] = application_data.portfolio_url
    if application_data.github_url:
        data["github_url"] = application_data.github_url

    resume_content = await resume.read()
    resume_name = resume.filename or "upload.bin"
    files = {
        "resume": (resume_name, resume_content, resume.content_type)
    }

    logger.debug("Prepared resume upload for filename=%s", resume_name)
    resume.file.seek(0)

    async with httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0)  # 60s total, 10s for connection
    ) as client:
        try:
            logger.info("Calling applications create endpoint")
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as http_err:
            logger.error(
                f"HTTP status error: {http_err.response.status_code}, "
                f"body={http_err.response.text}"
            )
            raise
        except httpx.RequestError as req_err:
            logger.error(f"Request error: {req_err}")
            raise

async def store_form_question_answer(
        application_id: UUID,
        question_answer: QAResponse
) -> dict:
    """
    Calls the Applications API to store a question-answer.

    Args:
        application_id (UUID): The application ID.
        question_answer (QAResponse): The question and answer data.

    Returns:
        dict: The JSON response from the gateway API.
    """
    applications_base_url = _get_applications_base_url()
    url = f"{applications_base_url}/{application_id}/form_question_answer"

    # The request body is the QAResponse converted to a dictionary.
    qa_payload = question_answer.model_dump()

    async with httpx.AsyncClient() as client:
        try:
            logger.info("Calling form_question_answer endpoint for application_id=%s", application_id)
            response = await client.post(url, json=qa_payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise

async def complete_application(
        application_id: UUID
):
    """
    Calls the Applications API to complete an application.

    Args:
        application_id (UUID): The application ID.

    Returns:
        dict: The JSON response from the gateway API.
    """
    # Construct the URL with application_id as a path parameter.
    applications_base_url = _get_applications_base_url()
    url = f"{applications_base_url}/{application_id}/complete/"

    async with httpx.AsyncClient() as client:
        try:
            logger.info("Calling complete endpoint for application_id=%s", application_id)
            response = await client.post(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise