from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from common.models_schemas.models import (Application)

def retrieve_job_id_by_application_id(application_id: UUID, db_session: Session):
    """
    Retrieves the job_id associated with a given application_id.
    """
    try:
        stmt = select(Application.job_id).where(Application.application_id == application_id)
        job_id = db_session.execute(stmt).scalar_one_or_none()

        return job_id
    except Exception as e:
        print(f"Error retrieving job_id for application_id {application_id}: {e}")
        return None