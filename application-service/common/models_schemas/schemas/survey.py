from pydantic import BaseModel
from typing import Optional, List
from dataclasses import dataclass
from uuid import UUID

class Survey(BaseModel):
    questions: List[str]

@dataclass
class ScoredQuestion:
    question: str
    score: Optional[int]

class QAResponse(BaseModel):
    question: str
    answer: str