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


# Import from other schema files to avoid duplication
from .user import UserResponse
from .admin import MessageResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "Invalid email format"
            }
        }
