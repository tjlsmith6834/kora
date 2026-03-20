import os
import httpx
import logging
from uuid import UUID
from ..schemas import QAResponse

logger = logging.getLogger(__name__)


def _get_applications_base_url() -> str:
    applications_base_url = os.getenv("APPLICATIONS_SERVICE_BASE_URL")
    if not applications_base_url:
        raise ValueError("APPLICATIONS_SERVICE_BASE_URL is not set")
    return applications_base_url


async def submit_question_answer_gateway(
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
    url = f"{applications_base_url}/{application_id}/question_answer/"

    # The request body is the QAResponse converted to a dictionary.
    qa_payload = question_answer.model_dump()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            logger.info("Calling question_answer endpoint for application_id=%s", application_id)
            response = await client.post(url, json=qa_payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise