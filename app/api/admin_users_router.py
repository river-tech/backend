from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.models.user import User
from app.models.purchase import Purchase
from app.models.workflow import Workflow
from app.models.invoice import Invoice
from app.schemas.user import (
    UserSearchResponse, 
    UserDetailResponse, 
    UserBanRequest,
    UserOverviewResponse,
    PurchaseHistoryItem,
    UserSearchRequest
)
from app.schemas.admin import MessageResponse
from app.api.auth_router import get_current_user
from fastapi import HTTPException, status

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

router = APIRouter(prefix="/api/admin/users", tags=["Admin - User Management"])

@router.get("/", response_model=List[UserSearchResponse])
async def get_all_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (no filters)."""
    try:
        users = db.query(User).filter(User.role == "USER").all()

        result: List[UserSearchResponse] = []
        for user in users:
            purchases = db.query(Purchase).filter(
                Purchase.user_id == user.id,
                Purchase.status == "ACTIVE"
            ).all()

            total_spent = sum(float(p.workflow.price) for p in purchases)

            result.append(UserSearchResponse(
                id=str(user.id),
                avatar_url=user.avatar_url,
                name=user.name,
                email=user.email,
                created_at=user.created_at.isoformat() if user.created_at else "",
                purchases_count=len(purchases),
                total_spent=total_spent,
                is_banned=bool(user.is_deleted)
            ))

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.get("/overview", response_model=UserOverviewResponse)
async def get_users_overview(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get users overview"""
    try:
        # Total users (exclude admins)
        total_users = db.query(User).filter(User.role == "USER").count()
        
        # Active users (not deleted)
        active_users = db.query(User).filter(
            User.role == "USER",
            User.is_deleted == False
        ).count()
        
        # Total purchases
        total_purchases = db.query(Purchase).filter(
            Purchase.status == "ACTIVE"
        ).count()
        
        # Total spent
        total_spent_result = db.query(func.sum(Workflow.price)).join(
            Purchase, Workflow.id == Purchase.workflow_id
        ).filter(Purchase.status == "ACTIVE").scalar()
        
        total_spent = float(total_spent_result) if total_spent_result else 0.0
        
        return UserOverviewResponse(
            total_users=total_users,
            active_users=active_users,
            total_purchases=total_purchases,
            total_spent=total_spent
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users overview: {str(e)}"
        )

@router.post("/search", response_model=List[UserSearchResponse])
async def search_users(
    search_data: Optional[UserSearchRequest] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Search users by name and banned status using POST body"""
    try:
        # Base query for users (exclude admins)
        query = db.query(User).filter(User.role == "USER")
        
        if search_data:
            # Filter by name if provided
            if search_data.name and search_data.name.strip():
                query = query.filter(User.name.ilike(f"%{search_data.name.strip()}%"))
            
            # Filter by banned status if provided
            if search_data.is_banned is not None:
                query = query.filter(User.is_deleted == search_data.is_banned)
        
        users = query.all()
        
        result = []
        for user in users:
            # Get purchase statistics
            purchases = db.query(Purchase).filter(
                Purchase.user_id == user.id,
                Purchase.status == "ACTIVE"
            ).all()
            
            total_spent = sum(float(purchase.workflow.price) for purchase in purchases)
            
            result.append(UserSearchResponse(
                id=str(user.id),
                avatar_url=user.avatar_url,
                name=user.name,
                email=user.email,
                created_at=user.created_at.isoformat() if user.created_at else "",
                purchases_count=len(purchases),
                total_spent=total_spent,
                is_banned=bool(user.is_deleted)
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user detail"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.role == "USER"
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get purchase statistics
        purchases = db.query(Purchase).filter(
            Purchase.user_id == user.id,
            Purchase.status == "ACTIVE"
        ).options(joinedload(Purchase.workflow)).all()
        
        total_spent = sum(float(purchase.workflow.price) for purchase in purchases)
        avg_order_value = total_spent / len(purchases) if purchases else 0
        
        # Get purchase history
        purchase_history = []
        for purchase in purchases:
            purchase_history.append(PurchaseHistoryItem(
                workflow_id=str(purchase.workflow.id),
                workflow_title=purchase.workflow.title,
                price=float(purchase.workflow.price),
                status="Active" if purchase.status == "ACTIVE" else "Expired",
                purchased_at=purchase.created_at.isoformat() if purchase.created_at else ""
            ))
        
        return UserDetailResponse(
            id=str(user.id),
            avatar_url=user.avatar_url,
            name=user.name,
            email=user.email,
            joined_at=user.created_at.isoformat() if user.created_at else "",
            status="Banned" if user.is_deleted else "Active",
            total_purchases=len(purchases),
            total_spent=total_spent,
            avg_order_value=avg_order_value,
            purchase_history=purchase_history
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user detail: {str(e)}"
        )

@router.patch("/{user_id}/ban", response_model=MessageResponse)
async def ban_unban_user(
    user_id: UUID,
    ban_data: UserBanRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ban or unban user"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.role == "USER"
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update ban status
        user.is_deleted = ban_data.is_deleted
        db.commit()
        db.refresh(user)
        
        action = "banned" if ban_data.is_deleted else "unbanned"
        return MessageResponse(
            success=True,
            message=f"User {action} successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user ban status: {str(e)}"
        )