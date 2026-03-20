import os
import httpx
from pydantic import ValidationError
from typing import Optional, List
from uuid import UUID
import logging

from .retrieve_job_id_by_application_id import retrieve_job_id_by_application_id

from common.models_schemas.models.application import Application
from common.models_schemas.schemas.rubric import Rubric as RubricSchema, RubricCategory as RubricCategorySchema, RubricCategoryEmbeddings as RubricCategoryEmbeddingsSchema

from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Tuple
import numpy as np
import logging

async def get_application_rubric_context(
    application_id: UUID, db_session: Session
) -> Tuple[UUID, RubricSchema, List[np.ndarray], List[np.ndarray]]:
    """
    Retrieve job_id, rubric, and embeddings for a given application.

    Returns:
        - job_id: UUID of the job associated with the application
        - rubric: Rubric object
        - focus_embeddings: List of focus embeddings (np.ndarray)
        - criteria_embeddings: List of criteria embeddings (np.ndarray)

    Raises:
        ValueError: if any required piece of data is missing
    """
    application = db_session.query(Application).get(application_id)

    job_id: UUID = retrieve_job_id_by_application_id(application_id, db_session)
    if not job_id:
        raise ValueError(f"❌ No job_id found for application_id: {application_id}")

    rubric: Optional[RubricSchema] = await retrieve_rubric_by_job_id(job_id)
    if not rubric or not rubric.categories:
        raise ValueError(f"❌ No rubric found for job_id: {job_id}")

    logging.info(f"Rubric: {rubric}")

    rubric_embeddings: List[RubricCategoryEmbeddingsSchema] = await get_embeddings(job_id)
    if not rubric_embeddings or len(rubric_embeddings) < 1:
        raise ValueError(f"❌ No rubric category embeddings found for job_id: {job_id}")

    focus_embeddings = [np.array(row.focus_embedding) for row in rubric_embeddings]
    criteria_embeddings = [np.array(row.criteria_embedding) for row in rubric_embeddings]

    return job_id, rubric, focus_embeddings, criteria_embeddings

async def retrieve_rubric_by_job_id(job_id: UUID) -> Optional[RubricSchema]:
    jobs_service_base_url=os.getenv("JOBS_API_URL")
    url = f"{jobs_service_base_url}/{job_id}/rubric"
    logging.info(f"Using base: {jobs_service_base_url}")
    logging.info(f"Requesting rubric from {url}")
    logging.info(f"Requesting rubric for job_id={job_id} from {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

        if response.status_code == 404:
            logging.warning(f"No rubric found for job_id={job_id}")
            return None

        response.raise_for_status()
        data = response.json()

        # Extract and validate only what we need
        rubric = RubricSchema(categories=[RubricCategorySchema(**cat) for cat in data["categories"]])
        logging.info(f"Successfully retrieved rubric for job_id={job_id}")
        return rubric

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error while retrieving rubric for job_id={job_id}: {e.response.status_code} - {e.response.text}")
        raise
    except httpx.RequestError as e:
        logging.error(f"Network error while retrieving rubric for job_id={job_id}: {e}")
        raise
    except ValidationError as e:
        logging.error(f"Response schema mismatch for rubric job_id={job_id}: {e}")
        raise
    except Exception as e:
        logging.exception(f"Unexpected error retrieving rubric for job_id={job_id}: {e}")
        raise

async def get_embeddings(job_id: UUID) -> List[RubricCategoryEmbeddingsSchema]:
    jobs_service_base_url=os.getenv("JOBS_API_URL")
    url = f"{jobs_service_base_url}/{job_id}/rubric/embeddings"
    logging.info(f"Requesting rubric for job_id={job_id} from {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

        if response.status_code == 404:
            logging.warning(f"No rubric embeddings found for job_id={job_id}")
            return []

        response.raise_for_status()
        data = response.json()

        embeddings = [RubricCategoryEmbeddingsSchema(**item) for item in data]
        logging.info(f"Retrieved {len(embeddings)} rubric embedding(s) for job_id={job_id}")
        return embeddings

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error while retrieving rubric for job_id={job_id}: {e.response.status_code} - {e.response.text}")
        raise
    except httpx.RequestError as e:
        logging.error(f"Network error while retrieving rubric for job_id={job_id}: {e}")
        raise
    except ValidationError as e:
        logging.error(f"Response schema mismatch for rubric job_id={job_id}: {e}")
        raise
    except Exception as e:
        logging.exception(f"Unexpected error retrieving rubric for job_id={job_id}: {e}")
        raise