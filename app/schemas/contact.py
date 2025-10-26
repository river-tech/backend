from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ContactRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=160, description="Full name is required")
    email: EmailStr = Field(..., description="Valid email is required")
    subject: str = Field(..., min_length=1, max_length=200, description="Subject is required")
    message: str = Field(..., min_length=1, description="Message is required")

class ContactResponse(BaseModel):
    id: str
    status: str
    message: Optional[str] = None

class ContactMessageResponse(BaseModel):
    id: str
    full_name: str
    email: str
    subject: Optional[str]
    message: str
    is_resolved: bool
    created_at: str

class ContactUpdateRequest(BaseModel):
    is_resolved: bool
