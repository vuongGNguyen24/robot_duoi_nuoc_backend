from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class StandardErrorFormat(BaseModel):
    error_code: str
    message: str
    details: list = None
