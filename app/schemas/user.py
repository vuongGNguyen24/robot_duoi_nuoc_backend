from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str = Field(..., description="Role of the user: 'admin' or 'user'")
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class SendOtpRequest(BaseModel):
    phone_number: str


class UpdatePhoneRequest(BaseModel):
    phone_number: str

class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class VerifyOtpRequest(BaseModel):
    phone_number: str
    otp: str
