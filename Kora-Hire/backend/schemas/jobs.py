from pydantic import BaseModel
from uuid import UUID
from typing import List

class RubricCategoryIn(BaseModel):
    """Represents a rubric category with multiple criteria."""
    category: str
    criteria: List[str]
    weight: float
    focus: str

class RubricIn(BaseModel):
    """Response model for the retrieved rubric."""
    categories: List[RubricCategoryIn]

class RubricCategory(BaseModel):
    """Represents a rubric category with multiple criteria."""
    category_id: UUID
    category: str
    criteria: List[str]
    weight: float
    focus: str

class Rubric(BaseModel):
    """Response model for the retrieved rubric."""
    categories: List[RubricCategory]

class JobFrame(BaseModel):
    title: str

class JobIn(BaseModel):
    organization_id: UUID
    title: str

class Job(BaseModel):
    job_id: UUID
    title: str
    organization_id: UUID

class JobList(BaseModel):
    jobs: List[Job]

class FormQuestionsIn(BaseModel):
    questions: List[str]

class FormQuestion(BaseModel):
    id: UUID
    question: str

class FormQuestionsOut(BaseModel):
    job_id: UUID
    questions: List[FormQuestion]