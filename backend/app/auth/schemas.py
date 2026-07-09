# app/auth/schemas.py
# Pydantic schemas define the shape of API requests and responses.
# These are DIFFERENT from SQLAlchemy models.
# SQLAlchemy models = database shape
# Pydantic schemas = API input/output shape
# Key difference: schemas never expose password_hash to the outside world

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    college: str
    department: str
    cgpa: Optional[str] = None
    graduation_year: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    college: Optional[str] = None
    department: Optional[str] = None
    target_company: Optional[str] = None
    created_at: datetime

    # This allows Pydantic to read from SQLAlchemy model attributes
    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse