from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DashboardResponse(BaseModel):
    total_workflows: int
    purchased_workflows: int
    total_spent: float
    recent_purchases: List[dict]

class ProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    avatar_url: Optional[str]
    created_at: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileUpdateResponse(BaseModel):
    success: bool
    message: str
    profile: ProfileResponse
