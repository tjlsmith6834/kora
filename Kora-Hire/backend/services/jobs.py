import os
import httpx
from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from typing import Tuple, Optional
from uuid import UUID
import logging

from schemas import JobFrame, Job, JobList, RubricIn, RubricCategory, Rubric
from schemas.jobs import FormQuestionsOut, FormQuestionsIn

logger = logging.getLogger(__name__)

jobs_service_base_url = os.getenv("JOBS_SERVICE_BASE_URL")
if not jobs_service_base_url:
    raise ValueError("JOBS_SERVICE_BASE_URL is not set")

async def store_job(new_job_data: JobFrame, organization_id: UUID) -> Job:
    url=f"{jobs_service_base_url}/"
    logging.info(f"Storing job via gateway {url}")

    async with httpx.AsyncClient() as client:
        try:
            new_job = jsonable_encoder({
                "title": new_job_data.title,
                "organization_id": organization_id,
            })
            resp = await client.post(
                url,
                json = new_job,
                timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        data = resp.json()
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    try:
        # Build our Pydantic models
        return Job(**data)
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")

async def fetch_job_by_organization_id(organization_id: UUID) -> JobList:
    url = f"{jobs_service_base_url}/?organization_id={organization_id}"
    logging.info(f"Fetching jobs from gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        data = resp.json()
        job_list = data.get("jobs")
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    try:
        # Build our Pydantic models
        job_list_return = []
        for j in job_list:
            job_list_return.append(Job(**j))
        return JobList(jobs=job_list_return)
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")


async def fetch_job_by_job_id(job_id: UUID) -> Job:
    url = f"{jobs_service_base_url}/{job_id}"
    logging.info(f"Fetching job from gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        job_raw = resp.json()
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")
    try:
        # Build our Pydantic models
        return Job(**job_raw)
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")


async def store_job_rubric_by_job_id(job_id: UUID, new_rubric: RubricIn) -> Rubric:
    url = f"{jobs_service_base_url}/{job_id}/rubric"
    logging.info(f"Storing rubric via gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            logging.info(f"new_rubric: {new_rubric.model_dump()}")
            resp = await client.post(
                url,
                json = new_rubric.model_dump(),
                timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        data = resp.json()
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    raw_categories = data.get("categories")
    if raw_categories is None:
        logging.error("Jobs service response missing 'categories' field")
        raise HTTPException(status_code=502, detail="Malformed response from jobs service")

    try:
        # Build our Pydantic models
        return Rubric(categories=[RubricCategory(**cat) for cat in raw_categories])
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")

async def fetch_job_rubric_by_job_id(job_id: UUID) -> Optional[Rubric]:
    url = f"{jobs_service_base_url}/{job_id}/rubric"
    logging.info(f"Fetching rubric from gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        data = resp.json()
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    if data is None:
        return None

    raw_categories = data.get("categories")
    if raw_categories is None:
        return None

    try:
        # Build our Pydantic models
        return Rubric(categories=[RubricCategory(**cat) for cat in raw_categories])
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")

async def store_job_description_by_job_id(job_id: UUID, job_description: UploadFile) -> Tuple[str, str]:
    url = f"{jobs_service_base_url}/{job_id}/description"
    logger.info(f"Storing job description via gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            file_contents = await job_description.read()
            file_name = job_description.filename or "upload.bin"
            jd_mapping = {
                "job_description_file": (file_name, file_contents, job_description.content_type)
            }
            resp = await client.post(url,files=jd_mapping, timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        data = resp.json()
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    try:
        file_url = data.get("file_url")
        file_name = data.get("file_name")
        return file_url, file_name
    except Exception as exc:
        logger.warning(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")

async def retrieve_job_description_file_name_by_job_id(job_id: UUID) -> str:
    url = f"{jobs_service_base_url}/{job_id}/description/file_name"
    logging.info(f"Storing job description via gateway: {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        response_raw = resp.json()
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")
    try:
        return response_raw["content"]
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")

async def store_form_questions(job_id: UUID, form_questions: FormQuestionsIn) -> FormQuestionsOut:
    url=f"{jobs_service_base_url}/{str(job_id)}/form_questions"
    logging.info(f"Storing form questions via gateway {url}")

    async with httpx.AsyncClient() as client:
        try:
            questions = form_questions.model_dump()
            resp = await client.post(
                url,
                json = questions,
                timeout=10.0)
            # Raises httpx.HTTPStatusError for 4xx/5xx …

            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # upstream returned a 4xx or 5xx
            status_code = exc.response.status_code
            detail = exc.response.text or exc.response.reason_phrase
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        data = resp.json()
        logging.info(f"Backend response: {data} ({type(data)})")
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    try:
        # Build our Pydantic models
        return FormQuestionsOut(**data)
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")

async def retrieve_form_questions(job_id: UUID) -> FormQuestionsOut:
    url=f"{jobs_service_base_url}/{str(job_id)}/form_questions"
    logging.info(f"Getting form questions via gateway {url}")

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
            logging.error(f"Jobs service HTTP error {status_code}: {detail}")
            raise HTTPException(status_code=status_code, detail=f"Jobs service error: {detail}")
        except httpx.RequestError as exc:
            # network problem, DNS failure, timeout, etc.
            logging.error(f"Error connecting to jobs service: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Unable to reach jobs service, please try again later."
            )
    try:
        data = resp.json()
        logging.info(f"Backend response: {data} ({type(data)})")
    except ValueError:
        logging.error("Invalid JSON from jobs service")
        raise HTTPException(status_code=502, detail="Invalid response from jobs service")

    try:
        # Build our Pydantic models
        return FormQuestionsOut(**data)
    except Exception as exc:
        logging.error(f"Failed to validate jobs payload: {exc}")
        raise HTTPException(status_code=502, detail="Unexpected data format from jobs service")