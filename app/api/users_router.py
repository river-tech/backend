from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.purchase import Purchase
from app.models.workflow import Workflow
from app.models.favorite import Favorite
from app.api.auth_router import get_current_user
from app.models.user import User
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
import os
import uuid
from datetime import datetime

router = APIRouter()

class DashboardResponse(BaseModel):
    total_purchases: int
    total_spent: float
    active_workflows: int
    saved_workflows: int

class ProfileResponse(BaseModel):
    id: str
    avatar_url: str
    name: str
    email: str
    created_at: datetime

class ProfileUpdateResponse(BaseModel):
    success: bool
    message: str
    user: dict

@router.get("/dashboard", response_model=DashboardResponse)
async def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard statistics"""
    try:
        # Check if user is accessing their own dashboard
        # Get total purchases
        total_purchases = db.query(func.count(Purchase.id))\
            .filter(Purchase.user_id == current_user.id)\
            .scalar() or 0
        # Get total spent
        total_spent = db.query(func.sum(Purchase.amount))\
            .filter(
                Purchase.user_id == current_user.id,
                Purchase.status == "ACTIVE"
            )\
            .scalar() or 0.0
        # Get active workflows (purchased and active)
        active_workflows = db.query(func.count(Purchase.id))\
            .filter(
                Purchase.user_id == current_user.id,
                Purchase.status == "ACTIVE"
            )\
            .scalar() or 0
        # Get saved workflows (favorites)
        saved_workflows = db.query(func.count(Favorite.id))\
            .filter(Favorite.user_id == current_user.id)\
            .scalar() or 0
        
        return DashboardResponse(
            total_purchases=total_purchases,
            total_spent=float(total_spent),
            active_workflows=active_workflows,
            saved_workflows=saved_workflows
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard data: {str(e)}"
        )

@router.get("/profile", response_model=ProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile information"""
    try:
        # Check if user is accessing their own profile
    # Không cần kiểm tra user_id, đã xác thực qua token
        
        return ProfileResponse(
            id=str(current_user.id),
            avatar_url=current_user.avatar_url or "",
            name=current_user.name,
            email=current_user.email,
            created_at=current_user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )

from pydantic import BaseModel

class ProfileUpdateRequest(BaseModel):
    avatar_url: Optional[str] = None
    name: Optional[str] = None

@router.patch("/profile", response_model=ProfileUpdateResponse)
async def update_user_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Check if user is updating their own profile
    # Không cần kiểm tra user_id, đã xác thực qua token
        
        # Update name if provided
        if body.name is not None:
            current_user.name = body.name
        # Update avatar_url if provided
        if body.avatar_url is not None:
            current_user.avatar_url = body.avatar_url
        
        db.commit()
        db.refresh(current_user)
        
        return ProfileUpdateResponse(
            success=True,
            message="Profile updated successfully",
            user={
                "id": str(current_user.id),
                "avatar_url": current_user.avatar_url or "",
                "name": current_user.name,
                "email": current_user.email
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
