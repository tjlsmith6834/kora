from pydantic import BaseModel
from uuid import UUID

class User(BaseModel):
    user_id: UUID
    org_id: UUID
    role: str