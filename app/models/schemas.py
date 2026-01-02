from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    """Schema for signup and login requests."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class Token(BaseModel):
    """Schema for the JWT response."""
    access_token: str
    token_type: str

class QuestionResponse(BaseModel):
    """Schema for the final generated output."""
    user: str
    job_role: str
    questions: str