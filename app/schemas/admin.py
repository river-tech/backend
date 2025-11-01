from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# Admin Authentication Schemas
class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class AdminChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class AdminResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: str

# Generic Response Schema
class MessageResponse(BaseModel):
    success: bool
    message: str

# Additional Admin Schemas
class AdminLoginResponse(BaseModel):
    success: bool
    token: str
    user: dict
    expires_in: int

class CreateAdminRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class CreateAdminResponse(BaseModel):
    id: str
    success: bool
    message: str

class DeleteAdminRequest(BaseModel):
    adminPassword: str

class DeleteAdminResponse(BaseModel):
    success: bool
    message: str

class ChangePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str

class ChangePasswordResponse(BaseModel):
    success: bool
    message: str


class AdminUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)