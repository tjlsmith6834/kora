from pydantic import BaseModel, field_serializer
from uuid import UUID
from typing import List, Optional
from datetime import date

class ProfileSummaryBullet(BaseModel):
    order: int
    detail: str

class ProfileBullets(BaseModel):
    liked_bullets: List[ProfileSummaryBullet]
    disliked_bullets: List[ProfileSummaryBullet]

class ProfileOverallScore(BaseModel):
    profile_score: int
    headline: str

class ProfileCategoryScore(BaseModel):
    category_id: UUID
    category_score: int
    category_score_reason: str

class ProfileRubric(BaseModel):
    category_scores: List[ProfileCategoryScore]

class RoleSummary(BaseModel):
    title: str
    company: str
    tenure: int

class ProfileCareerPath(BaseModel):
    years_of_experience: int
    most_recent_role: RoleSummary
    longest_tenured_role: RoleSummary
    average_tenure: int
    number_promotions: int

class RecentRole(BaseModel):
    id: UUID
    application_id: UUID
    title: str
    organization: str
    recency: int
    end_date: Optional[date] = None
    start_date: date

    @field_serializer("start_date", when_used="json")
    def serialize_start_date(self, value: date) -> str:
        return value.strftime("%B %Y")  # e.g. "January 2024"

    @field_serializer("end_date", when_used="json")
    def serialize_end_date(self, value: Optional[date]) -> str:
        if value is None:
            return "Current"
        return value.strftime("%B %Y")

class Profile(BaseModel):
    profile_id: UUID
    application_id: UUID
    applicant_name: str
    applicant_email: str
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]
    applicant_career: ProfileCareerPath
    profile_score: ProfileOverallScore
    profile_bullets: ProfileBullets
    profile_rubric: ProfileRubric
    recent_roles: Optional[List[RecentRole]]

