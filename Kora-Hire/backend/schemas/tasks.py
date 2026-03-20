from pydantic import BaseModel
from typing import Optional, Any

class Task(BaseModel):
    task_id: str
    state: str
    result: Optional[Any]