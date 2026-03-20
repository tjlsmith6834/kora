from pydantic import BaseModel, Field
from uuid import UUID
from typing import List

class JobIn(BaseModel):
    title: str = Field(..., description="Title of the job.")
    organization_id: UUID = Field(..., description="UUID for the organization.")

class JobOut(BaseModel):
    job_id: UUID
    title: str
    organization_id: UUID

class JobOutList(BaseModel):
    jobs: List[JobOut]

class FormQuestionsIn(BaseModel):
    questions: List[str]

class FormQuestion(BaseModel):
    id: UUID
    question: str

class FormQuestionsOut(BaseModel):
    job_id: UUID
    questions: List[FormQuestion]

class LinkConfig(BaseModel):
    require_linkedin: bool
    require_portfolio: bool
    require_github: bool



