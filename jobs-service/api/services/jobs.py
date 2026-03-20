from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from uuid import UUID, uuid4

from common.models_schemas.models import Job as JobDB
from common.models_schemas.models.jobs import FormQuestion as FormQuestionDB
from common.models_schemas.schemas import JobIn, JobOut, JobOutList
from common.models_schemas.schemas.jobs import FormQuestionsIn, FormQuestionsOut, FormQuestion, LinkConfig

logger = logging.getLogger(__name__)

async def store_job(
        job_in: JobIn,
        db_session: Session
) -> JobOut:
    try:
        new_job = JobDB(
            title=str(job_in.title),
            organization_id=job_in.organization_id
        )
        db_session.add(new_job)
        db_session.flush()
        job_id = new_job.job_id
        db_session.commit()
        return JobOut(
            job_id=job_id,
            title=str(job_in.title),
            organization_id=job_in.organization_id
        )

    except Exception as e:
        db_session.rollback()  # Rollback in case of failure
        raise RuntimeError(f"Error storing job: {e}")

async def retrieve_job(
        job_id: UUID,
        db_session: Session
) -> JobOut:
    try:
        job_db = db_session.query(JobDB).filter(JobDB.job_id == job_id).one()
        job = JobOut(
            title=job_db.title,
            organization_id=job_db.organization_id,
            job_id=job_db.job_id
        )
        logger.info(f"Retrieved job: {job}")
        return job
    except Exception as e:
        raise RuntimeError(f"Error retrieving job: {e}")

async def fetch_jobs_by_organization_id(
        organization_id: UUID,
        db_session: Session
) -> JobOutList:
    try:
        # Query jobs based on organization_id
        jobs = db_session.query(JobDB).filter(JobDB.organization_id == organization_id).all()
        job_list = [
            JobOut(
                title = job.title,
                organization_id = job.organization_id,
                job_id = job.job_id
            )
        for job in jobs
        ]
        logger.info(f"Found {len(job_list)} jobs")
        return JobOutList(
            jobs = job_list
        )
    except Exception as e:
        raise RuntimeError(f"Error retrieving jobs: {e}")

async def store_form_questions(
    job_id: UUID,
    form_questions: FormQuestionsIn,
    db_session: Session
) -> FormQuestionsOut:
    try:
        db_session.execute(
            delete(FormQuestionDB).where(FormQuestionDB.job_id == job_id)
        )
        questions_out = []
        for question in form_questions.questions:
            new_id = uuid4()
            question_db = FormQuestionDB(
                id=new_id,
                job_id=job_id,
                question=question,
            )
            db_session.add(question_db)
            questions_out.append(FormQuestion(id=new_id, question=question))

        db_session.commit()

        return FormQuestionsOut(
            job_id=job_id,
            questions=questions_out
        )

    except SQLAlchemyError as db_err:
        logger.exception(f"❌ SQLAlchemy error while storing questions: {db_err}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while storing questions: {db_err}")
    except Exception as e:
        db_session.rollback()
        logger.exception(f"❌ Unexpected error while storing questions: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error storing form questions: {e}")

async def fetch_form_questions(
    job_id: UUID,
    db_session: Session
) -> FormQuestionsOut:
    try:
        # Query the database for all questions for this job_id
        question_rows = db_session.query(FormQuestionDB).filter(
            FormQuestionDB.job_id == job_id
        ).order_by(FormQuestionDB.id).all()

        # Convert to schema
        questions_out = [
            FormQuestion(id=row.id, question=row.question)
            for row in question_rows
        ]

        return FormQuestionsOut(
            job_id=job_id,
            questions=questions_out
        )

    except SQLAlchemyError as db_err:
        logger.exception(f"❌ SQLAlchemy error while fetching questions: {db_err}")
        raise HTTPException(status_code=500, detail=f"Database error while fetching questions: {db_err}")
    except Exception as e:
        logger.exception(f"❌ Unexpected error while fetching questions: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching form questions: {e}")


async def store_link_config(
    job_id: UUID,
    config: LinkConfig,
    db_session: Session
) -> None:
    try:
        job: JobDB = db_session.execute(
            select(JobDB).where(JobDB.job_id == job_id)
        ).scalar_one_or_none()

        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        job.require_linkedin = config.require_linkedin
        job.require_portfolio = config.require_portfolio
        job.require_github = config.require_github

        db_session.commit()

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.exception(f"❌ SQLAlchemy error while storing link config: {db_err}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while storing link config: {db_err}")
    except Exception as e:
        db_session.rollback()
        logger.exception(f"❌ Unexpected error while storing link config: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error storing link config: {e}")

async def fetch_link_config(
    job_id: UUID,
    db_session: Session
) -> LinkConfig:
    try:
        # Load job row for link-config fields
        job: JobDB = db_session.execute(
            select(JobDB).where(JobDB.job_id == job_id)
        ).scalar_one_or_none()

        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        config_out = LinkConfig(
            require_linkedin=job.require_linkedin,
            require_portfolio=job.require_portfolio,
            require_github=job.require_github,
        )

        return config_out

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.exception(f"❌ SQLAlchemy error while fetching config: {db_err}")
        raise HTTPException(status_code=500, detail=f"Database error while fetching config: {db_err}")
    except Exception as e:
        logger.exception(f"❌ Unexpected error while fetching config: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching config: {e}")