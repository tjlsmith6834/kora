from collections import OrderedDict
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
from typing import Optional, List
from uuid import UUID, uuid4

from common.celery_config import celery_app
from common.models_schemas.models import Rubric as RubricDB, RubricCategory as RubricCategoryDB, RubricCriteria as RubricCriteriaDB, RubricCategoryEmbeddings as RubricCategoryEmbeddingsDB
from common.models_schemas.schemas import RubricOut as RubricOutSchema, RubricCategoryOut as CategoryOutSchema, RubricIn as RubricInSchema, RubricCategoryEmbeddingsOut as RubricCategoryEmbeddingsOutSchema

logger = logging.getLogger(__name__)

async def store_rubric(rubric_in: RubricInSchema, job_id: UUID, db: Session) -> RubricOutSchema:
    MAX_ATTEMPTS = 3
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with db.begin():  # start a transaction
                # Wipe old rows
                db.execute(
                    delete(RubricDB).where(RubricDB.job_id == job_id)
                )

                # Create the rubric
                new_rubric_id = uuid4()
                rubric_db = RubricDB(
                    rubric_id=new_rubric_id,
                    job_id=job_id,
                    status="pending"
                )
                db.add(rubric_db)

                out_categories: list[CategoryOutSchema] = []
                for cat in rubric_in.categories:
                    new_cat_id = uuid4()
                    cat_db = RubricCategoryDB(
                        category_id=new_cat_id,
                        rubric_id=new_rubric_id,
                        category=cat.category,
                        weight=cat.weight,
                        focus=cat.focus
                    )
                    db.add(cat_db)

                    crit_texts = []
                    for crit_text in cat.criteria:
                        crit_db = RubricCriteriaDB(
                            criteria_id=uuid4(),
                            category_id=new_cat_id,
                            criterion=crit_text
                        )
                        db.add(crit_db)
                        crit_texts.append(crit_text)

                    out_categories.append(
                        CategoryOutSchema(
                            category_id=new_cat_id,
                            category=cat.category,
                            weight=cat.weight,
                            focus=cat.focus,
                            criteria=crit_texts
                        )
                    )

                tid = str(uuid4())
                rubric_db.analysis_task_id = tid
                db.add(rubric_db)

            celery_app.send_task(
                "tasks.create_store_rubric_embeddings_task",
                args=[str(rubric_db.rubric_id), tid],
                task_id=tid
            )

            return RubricOutSchema(
                rubric_id=new_rubric_id,
                categories=out_categories
            )

        except IntegrityError as ie:
            db.rollback()
            if getattr(ie.orig, "pgcode", None) == "23505":
                # UUID collision, retry
                continue
            raise
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Failed to store rubric")
            raise

    raise RuntimeError("Could not store rubric after multiple UUID collisions")


async def fetch_rubric_by_job_id(job_id: UUID, db_session: Session) -> Optional[RubricOutSchema]:
    logger.info(f"Running fetch_rubric_by_job_id for job_id: {job_id}")

    try:
        stmt = (
            select(
                RubricDB.rubric_id,
                RubricCategoryDB.category_id,
                RubricCategoryDB.category,
                RubricCategoryDB.focus,
                RubricCategoryDB.weight,
                RubricCriteriaDB.criterion,
            )
            .select_from(RubricDB)
            .join(RubricCategoryDB, RubricDB.rubric_id == RubricCategoryDB.rubric_id)
            .join(RubricCriteriaDB, RubricCategoryDB.category_id == RubricCriteriaDB.category_id)
            .where(RubricDB.job_id == job_id)
        )

        logger.debug(f"Executing query for rubric with job_id={job_id}")
        rows = db_session.execute(stmt).all()
        logger.info(f"Query executed, retrieved {len(rows)} rows")

        if not rows:
            logger.warning(f"No rubric data found for job_id={job_id}")
            return None

        retrieved_rubric_id = rows[0].rubric_id
        logger.debug(f"Retrieved rubric_id: {retrieved_rubric_id}")

        categories: "OrderedDict[UUID, dict]" = OrderedDict()
        for (_rubric_id, category_id, category, focus, weight, criterion) in rows:
            if category_id not in categories:
                categories[category_id] = {
                    "category_id": category_id,
                    "category": category,
                    "focus": focus,
                    "weight": weight,
                    "criteria": [],
                }
            categories[category_id]["criteria"].append(criterion)

        pydantic_categories = [
            CategoryOutSchema(**cat_data) for cat_data in categories.values()
        ]

        logger.info(f"Successfully constructed RubricOutSchema for job_id={job_id}")

        rubric = RubricOutSchema(
            rubric_id=retrieved_rubric_id,
            categories=pydantic_categories
        )

        return rubric

    except ValidationError as ve:
        logger.error(f"❌ Pydantic validation error while constructing schema: {ve}")
        raise ValueError(f"Schema validation error: {ve}")
    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.exception(f"❌ SQLAlchemy error while fetching rubric for job_id={job_id}: {db_err}")
        raise HTTPException(status_code=500, detail="Database error while retrieving rubric.")
    except Exception as e:
        logger.exception(f"❌ Unexpected error fetching rubric for job_id={job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error retrieving rubric.")


async def retrieve_rubric_category_embeddings_by_job_id(
    job_id: UUID, db_session: Session
) -> List[RubricCategoryEmbeddingsOutSchema]:
    """
    Retrieves rubric category embeddings for a given job_id.

    Args:
        job_id (UUID): The job ID to query.
        db_session (Session): SQLAlchemy database session.

    Returns:
        List[RubricCategoryEmbeddingsOut]: List of embedding schemas.
    """
    try:
        logger.info(f"🔍 Retrieving rubric category embeddings for job_id={job_id}")

        stmt = (
            select(
                RubricCategoryEmbeddingsDB.embedding_id,
                RubricCategoryDB.category_id,
                RubricCategoryEmbeddingsDB.focus_embedding,
                RubricCategoryEmbeddingsDB.criteria_embedding,
            )
            .join(RubricDB, RubricCategoryDB.rubric_id == RubricDB.rubric_id)
            .join(RubricCategoryEmbeddingsDB, RubricCategoryDB.category_id == RubricCategoryEmbeddingsDB.category_id)
            .where(RubricDB.job_id == job_id)
        )

        results = db_session.execute(stmt).fetchall()

        embeddings = [
            RubricCategoryEmbeddingsOutSchema(
                embedding_id=row.embedding_id,
                category_id=row.category_id,
                focus_embedding=row.focus_embedding,
                criteria_embedding=row.criteria_embedding,
            )
            for row in results
        ]

        if not embeddings or len(embeddings) < 1:
            logger.warning(f"⚠️ No rubric embeddings found for job_id={job_id}")

        return embeddings

    except ValidationError as ve:
        logger.error(f"❌ Pydantic validation error while constructing schema: {ve}")
        raise ValueError(f"Schema validation error: {ve}")
    except HTTPException:
        raise
    except SQLAlchemyError as sae:
        logger.exception(f"❌ SQLAlchemy error while retrieving rubric embeddings for job_id={job_id}")
        raise HTTPException(status_code=500, detail="Database error retrieving rubric category embeddings")

    except Exception as e:
        logger.exception(f"❌ Unexpected error while retrieving rubric embeddings for job_id={job_id}")
        raise HTTPException(status_code=500, detail="Unexpected error retrieving rubric category embeddings")