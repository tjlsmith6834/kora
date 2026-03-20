from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class QAResponse(BaseModel):
    question: str
    answer: str

class NewApplication(BaseModel):
    job_id: UUID
    last_name: str
    first_name: str
    email: str
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]

class FormQuestion(BaseModel):
    id: UUID
    question: str

class FormQuestionsOut(BaseModel):
    job_id: UUID
    questions: List[FormQuestion]

class FormQuestionList(BaseModel):
    job_id: UUID
    questions: List[str]

class LinkConfig(BaseModel):
    require_linkedin: bool
    require_portfolio: bool
    require_github: bool