import os
import httpx
from typing import List
from uuid import UUID
import logging
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import re

from schemas import ProfileCategoryScore, ProfileRubric, ProfileSummary, QAResponse

logger = logging.getLogger(__name__)

application_service_base_url = os.getenv("APPLICATIONS_SERVICE_BASE_URL")
if not application_service_base_url:
    raise ValueError("APPLICATIONS_SERVICE_BASE_URL is not set")

async def fetch_application_summary_by_application_id(application_id: UUID) -> ProfileSummary:
    url = f"{application_service_base_url}/{application_id}/analysis/summary"
    logger.info(f"Fetching profile from gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            profile_json = response.json()

            return ProfileSummary(**profile_json)

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise


async def fetch_application_summary_by_job_id(job_id: UUID) -> List[ProfileSummary]:
    """
    Fetch all candidate profiles for a given job_id from the FastAPI gateway,
    and return them as a list of Pydantic Profile objects.
    """
    url = f"{application_service_base_url}/analysis/summary/?job_id={job_id}"
    logger.info(f"Fetching profiles by job_id from gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            response_json = response.json()
            logger.info("Fetched %s profile summaries for job_id=%s", len(response_json), job_id)

            profile_list = [ProfileSummary(**profile_json) for profile_json in response_json]

            return profile_list

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise

async def fetch_application_form_question_answers_by_application_id(application_id: UUID) -> List[QAResponse]:
    url = f"{application_service_base_url}/{application_id}/form_question_answer"
    logger.info(f"Fetching form question answers from gateway: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            response_json = response.json()

            qa_responses = [QAResponse(**response) for response in response_json]

            return qa_responses

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise


async def fetch_application_analysis_rubric_by_application_id(application_id: UUID) -> ProfileRubric:
    url = f"{application_service_base_url}/{application_id}/analysis/rubric"
    logger.info(f"Fetching profile from gateway: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            response_json = response.json()

            profile_rubric = ProfileRubric(
                category_scores=[ProfileCategoryScore(**category_score) for category_score in response_json]
            )
            return profile_rubric

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise

async def fetch_application_interview_question_answers_by_application_id(application_id: UUID) -> List[QAResponse]:
    url = f"{application_service_base_url}/{application_id}/interview_question_answers"
    logger.info(f"Fetching interview question answers from gateway: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            response_json = response.json()

            qa_responses = [QAResponse(**response) for response in response_json]

            return qa_responses

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise

async def submit_interview_question_answer(
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
    url = f"{application_service_base_url}/{application_id}/question_answer/"

    # The request body is the QAResponse converted to a dictionary.
    qa_payload = question_answer.model_dump()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            logger.info("Submitting interview question answer for application_id=%s", application_id)
            response = await client.post(url, json=qa_payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise

async def hide_application_by_application_id(application_id: UUID) -> None:
    url = f"{application_service_base_url}/{application_id}/hide/"
    logger.info(f"Hiding application via gateway {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.put(
                url,
                timeout=10.0
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logger.error(f"Applications service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Applications service error: {detail}")
        except httpx.RequestError as exc:
            logger.error(f"Error connecting to applications service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach applications service, please try again later."
            )

    return

async def fetch_resume_stream(application_id: UUID) -> StreamingResponse:
    url = f"{application_service_base_url}/{application_id}/resume/"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=30.0)
            resp.raise_for_status()

            # Extract filename if present
            content_disposition = resp.headers.get("content-disposition", "")
            match = re.search(r'filename="(.+?)"', content_disposition)
            filename = match.group(1) if match else "resume.pdf"

            async def stream_bytes():
                async for chunk in resp.aiter_bytes():
                    yield chunk

            return StreamingResponse(
                stream_bytes(),
                media_type=resp.headers.get("content-type", "application/pdf"),
                headers={
                    # Force inline display
                    "Content-Disposition": f'inline; filename="{filename}"'
                }
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Upstream error: {exc.response.text or exc.response.reason_phrase}"
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Connection error to application service: {str(exc)}"
            )
