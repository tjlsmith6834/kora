from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4, UUID
from typing import List
import logging

from common.models_schemas.models.profile import RecentRole as RecentRoleModel
from common.models_schemas.schemas.profiles import RecentRole as RecentRoleSchema

def store_candidate_career(
        application_id_in: UUID,
        career_path_in: List[RecentRoleSchema],
        db_session: Session):
    try:
        logging.info(f"Storing career for application_id: {application_id_in}")

        #Delete old RecentRoleModel listings
        db_session.query(RecentRoleModel).filter(
            RecentRoleModel.application_id == application_id_in
        ).delete(synchronize_session=False)

        # Step 2: Insert new RecentRoleModel records
        career_path_models = []
        for role in career_path_in:
            role_model = RecentRoleModel(
                id=uuid4(),
                application_id=application_id_in,
                title=role.title,
                organization=role.organization,
                start_date=role.start_date,
                end_date=role.end_date,
                recency=role.recency,
            )
            career_path_models.append(role_model)


        # Add role models
        db_session.add_all(career_path_models)
        db_session.flush()

        # Commit the transaction
        db_session.commit()
        logging.info(f"✅ Successfully stored career application_id: {application_id_in}")

    except SQLAlchemyError as e:
        db_session.rollback()
        logging.error(f"❌ Database error while storing career: {str(e)}")
        raise

    except Exception as e:
        db_session.rollback()
        logging.error(f"❌ Unexpected error: {str(e)}")
        raise