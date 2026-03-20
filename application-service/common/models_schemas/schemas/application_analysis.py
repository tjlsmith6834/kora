from pydantic import BaseModel
from uuid import UUID
from typing import List, Literal

class ScoredApplicationAnnotation(BaseModel):
    type: str
    comment: str
    evidence: List[str]
    alignment_level: Literal["high", "medium", "low"]
    alignment_level_reason: str

class ScoredApplicationAnnotationList(BaseModel):
    list: List[ScoredApplicationAnnotation]

class ApplicationAnalysisCategory2(BaseModel):
    category_id: UUID
    category: str
    annotations_with_scores: ScoredApplicationAnnotationList

class ApplicationAnalysisIn2(BaseModel):
    application_id: UUID
    category_analyses: List[ApplicationAnalysisCategory2]

class SummaryBullet(BaseModel):
    type: str
    order: int
    detail: str

class ApplicationAnalysisSummary(BaseModel):
    applicant_score: int
    applicant_score_interpretation: str
    strength_bullets: List[SummaryBullet]
    weakness_bullets: List[SummaryBullet]



