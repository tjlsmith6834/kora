from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from pgvector.sqlalchemy import Vector
from .base import Base
import uuid
from datetime import datetime

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = {"schema": "kora_applications"}  # Ensure schema matches

    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    candidate_first_name = Column(String, nullable=False)
    candidate_last_name = Column(String, nullable=True)
    candidate_email = Column(String, nullable=False)
    linkedin = Column(String, nullable=True)
    portfolio = Column(String, nullable=True)
    github = Column(String, nullable=True)
    application_status = Column(String)
    analysis_task_id =Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)

class ApplicationEmbedding(Base):
    __tablename__ = "application_embeddings"
    __table_args__ = {"schema": "kora_applications"}

    embedding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.applications.application_id"), nullable=False, index=True)
    embedding = Column(Vector(1536), nullable=False)  # Ensure correct vector size
    content = Column(String, nullable=False)

class ApplicationDocuments(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "kora_applications"}

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.applications.application_id"), nullable=False)
    file_url = Column(String, nullable=False)
    is_primary_resume = Column(Boolean, default=False)

class ApplicationQuestionsAnswers(Base):
    __tablename__ = "application_questions_answers"
    __table_args__ = {"schema": "kora_applications"}

    qa_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.applications.application_id"), nullable=False, index=True)
    question_text = Column(String, nullable=False)
    answer_text = Column(String)
    embeddings = Column(Vector(1536))
    embedding_content = Column(String)

class FormQuestionAnswers(Base):
    __tablename__ = "form_question_answers"
    __table_args__ = {"schema": "kora_applications"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.applications.application_id"), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String)