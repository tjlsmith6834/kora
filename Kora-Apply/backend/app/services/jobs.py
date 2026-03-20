import os
import httpx
from fastapi import HTTPException
from uuid import UUID
import logging

from ..schemas import FormQuestionsOut, FormQuestionList, LinkConfig

logger = logging.getLogger(__name__)


def _get_jobs_service_base_url() -> str:
    jobs_service_base_url = os.getenv("JOBS_SERVICE_BASE_URL")
    if not jobs_service_base_url:
        raise ValueError("JOBS_SERVICE_BASE_URL is not set")
    return jobs_service_base_url

async def retrieve_form_questions(job_id: UUID) -> FormQuestionList:
    jobs_service_base_url = _get_jobs_service_base_url()
    url=f"{jobs_service_base_url}/{str(job_id)}/form_questions"
    logger.info(f"Getting form questions via gateway {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                url,
                timeout=10.0)
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
        data = resp.json()
        logger.info(f"Backend response type={type(data)}")
    except ValueError:
        logger.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    try:
        service_model = FormQuestionsOut(**data)

        logger.info(
            "Form questions retrieved count=%s",
            len(service_model.questions),
        )

        simplified_questions = [q.question for q in service_model.questions]

        return FormQuestionList(
            job_id=service_model.job_id,
            questions=simplified_questions
        )
    except Exception as exc:
        logger.error(f"Failed to validate or transform jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")

async def retrieve_link_config(job_id: UUID) -> LinkConfig:
    jobs_service_base_url = _get_jobs_service_base_url()
    url=f"{jobs_service_base_url}/{str(job_id)}/link_config"
    logger.info(f"Getting link config via gateway {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                url,
                timeout=10.0)
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
        data = resp.json()
        logger.info(f"Link config backend response type={type(data)}")
    except ValueError:
        logger.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    try:
        return LinkConfig(**data)

    except Exception as exc:
        logger.error(f"Failed to validate or transform jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")