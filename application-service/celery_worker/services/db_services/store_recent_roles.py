from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging

from common.models_schemas.models.profile import RecentRole as RecentRoleModel
from common.models_schemas.schemas.profiles import RecentRole as RecentRoleSchema

def store_recent_roles_for_application(
    application_id: UUID,
    roles_in: List[RecentRoleSchema],
    db_session: Session,
) -> List[RecentRoleModel]:
    try:
        logging.info(f"Storing recent roles for application_id: {application_id}")

        # Delete old roles for this application
        db_session.query(RecentRoleModel).filter(
            RecentRoleModel.application_id == application_id
        ).delete(synchronize_session=False)

        models: list[RecentRoleModel] = []

        for role in roles_in:
            model = RecentRoleModel(
                id=uuid4(),
                application_id=application_id,
                title=role.title,
                organization=role.organization,
                recency=role.recency,
                start_date=role.start_date,
                end_date=role.end_date,
            )
            models.append(model)

        db_session.add_all(models)
        db_session.commit()
        logging.info(f"✅ Stored {len(models)} recent roles for {application_id}")
        return models

    except SQLAlchemyError as e:
        db_session.rollback()
        logging.error(f"❌ DB error while storing recent roles: {e}")
        raise
    except Exception as e:
        db_session.rollback()
        logging.error(f"❌ Unexpected error while storing recent roles: {e}")
        raise