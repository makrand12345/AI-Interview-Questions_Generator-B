from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class SeniorityLevel(str, Enum):
    fresher = "Fresher"
    experienced = "Experienced"
    mid_level = "Mid-level"
    senior = "Senior"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str