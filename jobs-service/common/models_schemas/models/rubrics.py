from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from .base import Base
import uuid

class Rubric(Base):
    __tablename__ = "rubrics"
    __table_args__ = {"schema": "kora_jobs"}

    rubric_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("kora_jobs.jobs.job_id"), nullable=False)
    status = Column(String, nullable=True)
    analysis_task_id = Column(UUID(as_uuid=True), nullable=True)


class RubricCategory(Base):
    __tablename__ = "rubric_categories"
    __table_args__ = {"schema": "kora_jobs"}

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rubric_id = Column(UUID(as_uuid=True), ForeignKey("kora_jobs.rubrics.rubric_id"), nullable=False, index=True)
    category = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    focus = Column(String, nullable=False)


class RubricCriteria(Base):
    __tablename__ = "rubric_criteria"
    __table_args__ = {"schema": "kora_jobs"}

    criteria_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("kora_jobs.rubric_categories.category_id"), nullable=False)
    criterion = Column(String(255), nullable=False)


class RubricCategoryEmbeddings(Base):
    __tablename__ = "rubric_category_embeddings"
    __table_args__ = {"schema": "kora_jobs"}

    embedding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("kora_jobs.rubric_categories.category_id"),
                         nullable=False, index=True)
    focus_embedding = Column(Vector(1536), nullable=False)  # OpenAI embeddings typically use 1536 dimensions
    criteria_embedding = Column(Vector(1536), nullable=False)