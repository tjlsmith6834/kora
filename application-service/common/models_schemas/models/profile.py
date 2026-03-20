import uuid
from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    __table_args__ = {"schema": "kora_applications"}  # Define the schema explicitly

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.applications.application_id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)

class CandidateProfileCategoryScore(Base):
    __tablename__ = "candidate_profile_category_scores"
    __table_args__ = {"schema": "kora_applications"}  # Ensure it's stored in the correct schema

    category_score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.candidate_profiles.profile_id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    reasoning = Column(Text, nullable=False)

class CandidateProfileSummaryBullet(Base):
    __tablename__ = "profile_bullets"
    __table_args__ = {"schema": "kora_applications"}  # Ensure it's stored in the correct schema

    bullet_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.candidate_profiles.profile_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    detail = Column(Text, nullable=False)

class CareerPath(Base):
    __tablename__ = "profile_career_paths"
    __table_args__ = {"schema": "kora_applications"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.candidate_profiles.profile_id"), nullable=False, unique=True)

    years_of_experience = Column(Integer, nullable=False)
    average_tenure = Column(Integer, nullable=False)
    number_promotions = Column(Integer, nullable=False)

    # Flattened summary of most recent role
    most_recent_title = Column(Text, nullable=False)
    most_recent_company = Column(Text, nullable=False)
    most_recent_tenure = Column(Integer, nullable=False)

    # Flattened summary of longest-tenured role
    longest_title = Column(Text, nullable=False)
    longest_company = Column(Text, nullable=False)
    longest_tenure = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class RecentRole(Base):
    __tablename__ = "recent_roles"
    __table_args__ = {"schema": "kora_applications"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("kora_applications.applications.application_id"), nullable=False, unique=True)
    title = Column(Text, nullable=False)
    organization = Column(Text, nullable=False)
    recency = Column(Integer, nullable=False)
    end_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=False)