from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class NewApplication(BaseModel):
    job_id: UUID
    last_name: str
    first_name: str
    email: str
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]