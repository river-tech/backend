from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
import uuid

from app.db.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.api.auth_router import get_current_user
from app.services.websocket_manager import manager

class NotificationCreateRequest(BaseModel):
    user_id: Optional[UUID] = Field(None, description="Specific user ID. If null, send to all users")
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: str = Field(..., pattern="^(SUCCESS|WARNING|ERROR)$")

class NotificationCreateResponse(BaseModel):
    success: bool
    message: str

class NotificationBroadcastRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: str = Field(..., pattern="^(SUCCESS|WARNING|ERROR)$")

class NotificationBroadcastResponse(BaseModel):
    success: bool
    message: str

router = APIRouter(prefix="/api/admin/notifications", tags=["Admin - Notifications"])

async def get_current_admin(current_user: User = Depends(get_current_user)):
    """Ensure current user is admin"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

@router.get("/")
async def get_admin_notifications(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all notifications for the current admin. Respond with array, not object."""
    try:
        notifications = db.query(Notification).filter(
            Notification.user_id == current_admin.id
        ).all()

        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "is_unread": notification.is_unread
            })
        return notifications_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )

class AdminNotificationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: str = Field(..., pattern="^(SUCCESS|WARNING|ERROR)$")

class AdminNotificationResponse(BaseModel):
    success: bool
    message: str

@router.post("/self", response_model=AdminNotificationResponse)
async def create_notification_for_current_admin(
    request: AdminNotificationRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a notification for the current admin."""
    try:
        notification = Notification(
            id=uuid.uuid4(),
            user_id=current_admin.id,
            title=request.title,
            message=request.message,
            type=request.type,
            is_unread=True
        )
        db.add(notification)
        db.commit()

        return AdminNotificationResponse(success=True, message="Notification created for current admin")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin notification: {str(e)}"
        )

@router.post("/admins/broadcast", response_model=NotificationBroadcastResponse)
async def broadcast_notification_to_all_admins(
    request: NotificationBroadcastRequest,
    db: Session = Depends(get_db)
):
    """Broadcast a notification to all admin users (no authentication required)."""
    try:
        admins = db.query(User).filter(User.role == "ADMIN").all()

        notifications_created = 0
        for admin in admins:
            notification = Notification(
                id=uuid.uuid4(),
                user_id=admin.id,
                title=request.title,
                message=request.message,
                type=request.type,
                is_unread=True
            )
            db.add(notification)
            notifications_created += 1

        db.commit()

        return NotificationBroadcastResponse(
            success=True,
            message=f"Notification broadcasted successfully to {notifications_created} admins"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast to admins: {str(e)}"
        )

@router.post("/", response_model=NotificationCreateResponse)
async def create_notification(
    request: NotificationCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create notification for specific user or all users"""
    try:
        notifications_created = 0
        
        if request.user_id:
            # Send to specific user
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            notification = Notification(
                id=uuid.uuid4(),
                user_id=request.user_id,
                title=request.title,
                message=request.message,
                type=request.type,
                is_unread=True
            )
            db.add(notification)
            notifications_created = 1
            db.commit()
            
            # Send WebSocket notification to specific user
            await manager.send_personal_message({
                "type": "notification",
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.type,
                "is_unread": notification.is_unread,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }, str(request.user_id))
            
        else:
            # Send to all users
            users = db.query(User).filter(User.role == "USER").all()
            
            notifications_list = []
            for user in users:
                notification = Notification(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    title=request.title,
                    message=request.message,
                    type=request.type,
                    is_unread=True
                )
                db.add(notification)
                notifications_list.append((notification, user.id))
                notifications_created += 1
            
            db.commit()
            
            # Send WebSocket notification to all users
            for notification, user_id in notifications_list:
                await manager.send_personal_message({
                    "type": "notification",
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.type,
                    "is_unread": notification.is_unread,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None
                }, str(user_id))
        
        return NotificationCreateResponse(
            success=True,
            message=f"Notification(s) created successfully for {notifications_created} user(s)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )

@router.post("/broadcast", response_model=NotificationBroadcastResponse)
async def broadcast_notification_to_all_users(
    request: NotificationBroadcastRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send notification to all users"""
    try:
        # Get all users (role = "USER")
        users = db.query(User).filter(User.role == "USER").all()
        
        notifications_list = []
        notifications_created = 0
        for user in users:
            notification = Notification(
                id=uuid.uuid4(),
                user_id=user.id,
                title=request.title,
                message=request.message,
                type=request.type,
                is_unread=True
            )
            db.add(notification)
            notifications_list.append((notification, user.id))
            notifications_created += 1
        
        db.commit()
        
        # Send WebSocket notification to all users
        for notification, user_id in notifications_list:
            await manager.send_personal_message({
                "type": "notification",
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.type,
                "is_unread": notification.is_unread,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }, str(user_id))
        
        return NotificationBroadcastResponse(
            success=True,
            message=f"Notification broadcasted successfully to {notifications_created} users"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast notification: {str(e)}"
        )

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_admin.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.is_unread = False
        db.commit()
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.patch("/read-all")
async def mark_all_notifications_read(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Mark all admin notifications as read"""
    try:
        # Update all unread notifications for this admin
        updated_count = db.query(Notification).filter(
            Notification.user_id == current_admin.id,
            Notification.is_unread == False
        ).update({"is_unread": True})
        
        db.commit()
        
        return {
            "success": True,
            "message": "All notifications marked as read"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )

@router.delete("/all")
async def delete_all_notifications(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete all admin notifications"""
    try:
        # Count notifications before deletion
        deleted_count = db.query(Notification).filter(
            Notification.user_id == current_admin.id
        ).count()
        
        # Delete all notifications for this admin
        db.query(Notification).filter(
            Notification.user_id == current_admin.id
        ).delete()
        
        db.commit()
        
        return {
            "success": True,
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all notifications: {str(e)}"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_admin.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        db.delete(notification)
        db.commit()
        
        return {
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )
