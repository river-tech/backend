from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.notification import Notification
from app.api.auth_router import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import List
from uuid import UUID

router = APIRouter()

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_unread: bool
    created_at: str

class MessageResponse(BaseModel):
    success: bool
    message: str

class DeleteAllResponse(BaseModel):
    success: bool
    deleted_count: int

@router.get("/", response_model=List[NotificationResponse])
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of notifications for current user"""
    try:
        notifications = db.query(Notification)\
            .filter(Notification.user_id == current_user.id)\
            .order_by(Notification.created_at.desc())\
            .all()
        
        result = []
        for notification in notifications:
            result.append(NotificationResponse(
                id=str(notification.id),
                title=notification.title,
                message=notification.message,
                type=notification.type,
                is_unread=notification.is_unread,
                created_at=notification.created_at.isoformat() if notification.created_at else None
            ))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )

@router.patch("/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.is_unread = False
        db.commit()
        
        return MessageResponse(
            success=True,
            message="Notification marked as read"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.delete("/all", response_model=DeleteAllResponse)
async def delete_all_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all notifications for current user"""
    try:
        # Count notifications before deletion
        deleted_count = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).count()
        
        # Delete all notifications
        db.query(Notification).filter(Notification.user_id == current_user.id).delete()
        db.commit()
        
        return DeleteAllResponse(
            success=True,
            deleted_count=deleted_count
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notifications: {str(e)}"
        )

@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        db.delete(notification)
        db.commit()
        
        return MessageResponse(
            success=True,
            message="Notification deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )
