from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_deleted: bool
    created_at: str

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)

class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar_url: Optional[str]
    created_at: str
    updated_at: str

class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str

class SetNewPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str = Field(..., min_length=6)

# Admin User Management Schemas
class UserSearchResponse(BaseModel):
    id: str
    avatar_url: Optional[str]
    name: str
    email: str
    created_at: str
    purchases_count: int
    total_spent: float
    is_banned: bool

class UserDetailResponse(BaseModel):
    id: str
    avatar_url: Optional[str]
    name: str
    email: str
    joined_at: str
    status: str  # "Active" | "Banned"
    total_purchases: int
    total_spent: float
    avg_order_value: float
    purchase_history: list

class PurchaseHistoryItem(BaseModel):
    workflow_id: str
    workflow_title: str
    price: float
    status: str  # "Active" | "Expired"
    purchased_at: str

class UserBanRequest(BaseModel):
    is_deleted: bool

class UserOverviewResponse(BaseModel):
    total_users: int
    active_users: int
    total_purchases: int
    total_spent: float

class UserSearchRequest(BaseModel):
    name: Optional[str] = None
    is_banned: Optional[bool] = None
