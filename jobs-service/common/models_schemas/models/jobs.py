from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "kora_jobs"}

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    title = Column(String, nullable=False)
    require_linkedin = Column(Boolean, nullable=True, default=False)
    require_portfolio = Column(Boolean, nullable=True, default=False)
    require_github = Column(Boolean, nullable=True, default=False)


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    __table_args__ = {"schema": "kora_jobs"}

    job_description_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_url = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("kora_jobs.jobs.job_id"), nullable=False)

class FormQuestion(Base):
    __tablename__ = "form_questions"
    __table_args__ = {"schema": "kora_jobs"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("kora_jobs.jobs.job_id"), nullable=False)
    question = Column(String)