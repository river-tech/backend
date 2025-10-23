from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_unread: bool
    created_at: str

class MessageResponse(BaseModel):
    success: bool
    message: str

class DeleteAllResponse(BaseModel):
    success: bool
    message: str
    deleted_count: int
