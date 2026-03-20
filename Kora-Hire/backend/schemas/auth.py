from pydantic import BaseModel

class TokenPayload(BaseModel):
    uid: str