from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """User registration request schema"""
    name: str
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str
    new_password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com"
            }
        }


class VerifyOTPRequest(BaseModel):
    """Verify OTP request schema"""
    email: EmailStr
    otp_code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "otp_code": "123456"
            }
        }


class SetNewPasswordRequest(BaseModel):
    """Set new password request schema"""
    email: EmailStr
    otp_code: str
    new_password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "otp_code": "123456",
                "new_password": "newpassword123"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    name: str
    email: str
    role: str
    is_deleted: bool
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "USER",
                "is_deleted": False,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response schema"""
    message: str
    success: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Invalid email format"
            }
        }
