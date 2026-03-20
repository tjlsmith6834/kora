from pydantic import BaseModel
from typing import Optional

class SimpleResponse(BaseModel):
    message: str
    content: Optional[str]