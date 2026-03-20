from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class ProfileCategoryScore(BaseModel):
    category_id: UUID
    category_score: int
    category_score_reason: str

class ProfileRubric(BaseModel):
    category_scores: List[ProfileCategoryScore]

class Profile(BaseModel):
    profile_id: UUID
    application_id: UUID
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    applicant_score: Optional[int] = None
    applicant_score_interpretation: Optional[str] = None
    category_analyses: Optional[List[ProfileCategoryScore]] = None

class ProfileList(BaseModel):
    profiles: List[Profile]

class ProfileSummaryBullet(BaseModel):
    order: int
    detail: str

class ProfileSummary(BaseModel):
    profile_id: UUID
    application_id: UUID
    applicant_name: str
    applicant_email: str
    applicant_score: int
    applicant_score_interpretation: str
    strength_bullets: List[ProfileSummaryBullet]
    weakness_bullets: List[ProfileSummaryBullet]

class QAResponse(BaseModel):
    question: str
    answer: str