from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.api.auth_router import get_current_user
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import bcrypt
import uuid
from app.schemas.admin import AdminUpdateRequest
router = APIRouter()

# Import schemas from schemas module
from app.schemas.admin import (
    AdminLoginRequest, AdminLoginResponse, AdminResponse, MessageResponse,
    CreateAdminRequest, CreateAdminResponse, DeleteAdminRequest, DeleteAdminResponse,
    ChangePasswordRequest, ChangePasswordResponse
)

# Helper function to check if user is admin
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

# Helper function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Helper function to hash password
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# 1. POST /api/admin/login - Login admin account
@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    login_data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """Login admin account"""
    try:
        # Find admin user by email
        admin = db.query(User).filter(
            User.email == login_data.email,
            User.role == "ADMIN"
        ).first()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT token (reuse existing auth logic)
        from app.services.auth import create_access_token
        from datetime import timedelta
        # Admin token expires in 1 hour
        access_token = create_access_token(data={"sub": str(admin.id)}, expires_delta=timedelta(hours=1))
        
        return AdminLoginResponse(
            success=True,
            token=access_token,
            user={
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email,
                "role": admin.role
            },
            expires_in=3600  # 1 hour
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

# 2. POST /api/admin/settings/admins - Create new admin account
@router.post("/settings/admins", response_model=CreateAdminResponse)
async def create_admin(
    admin_data: CreateAdminRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new admin account"""
    try:
        # Check if email already exists
        existing_admin = db.query(User).filter(User.email == admin_data.email).first()
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new admin
        new_admin = User(
            id=uuid.uuid4(),
            name=admin_data.name,
            email=admin_data.email,
            password_hash=hash_password(admin_data.password),
            role="ADMIN",
            is_deleted=False
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        return CreateAdminResponse(
            id=str(new_admin.id),
            success=True,
            message="Admin created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin: {str(e)}"
        )

# 3. GET /api/admin/settings/admins - Get all admin accounts
@router.get("/settings/admins", response_model=List[AdminResponse])
async def get_all_admins(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all admin accounts"""
    try:
        admins = db.query(User).filter(User.role == "ADMIN").all()
        
        return [
             AdminResponse(
                id=str(admin.id),
                name=admin.name,
                email=admin.email,
                role=admin.role,
                created_at=admin.created_at.isoformat() if admin.created_at else ""
            ) for admin in admins
        ]
           
        
            
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch admins: {str(e)}"
        )

# 4. DELETE /api/admin/settings/admins/:id - Delete admin account
@router.delete("/settings/admins/{admin_id}", response_model=DeleteAdminResponse)
async def delete_admin(
    admin_id: UUID,
    delete_data: DeleteAdminRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete admin account"""
    try:
        # Verify current admin password
        if not verify_password(delete_data.adminPassword, current_admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin password"
            )
        
        # Check if trying to delete self
        if admin_id == current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Find admin to delete
        admin_to_delete = db.query(User).filter(
            User.id == admin_id,
            User.role == "ADMIN"
        ).first()
        
        if not admin_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Delete admin
        db.delete(admin_to_delete)
        db.commit()
        
        return DeleteAdminResponse(
            success=True,
            message="Admin deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete admin: {str(e)}"
        )

# 5. PATCH /api/admin/settings/password - Change admin password
@router.patch("/settings/password", response_model=ChangePasswordResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Change admin password"""
    try:
        # Validate new password length manually to return simple detail string
        if password_data.newPassword is None or len(password_data.newPassword) < 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New password must be at least 6 characters"
            )

        # Verify current password
        if not verify_password(password_data.currentPassword, current_admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_admin.password_hash = hash_password(password_data.newPassword)
        
        db.commit()
        
        return ChangePasswordResponse(
            success=True,
            message="Password changed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

# 6. GET /api/admin/profile - Get admin profile
@router.get("/profile", response_model=AdminResponse)
async def get_admin_profile(
    current_admin: User = Depends(get_current_admin)
):
    """Get admin profile"""
    return AdminResponse(
        id=str(current_admin.id),
        name=current_admin.name,
        email=current_admin.email,
        role=current_admin.role,
        created_at=current_admin.created_at.isoformat() if current_admin.created_at else None
    )

# 7. PUT /api/admin/profile - Update admin profile
@router.put("/profile", response_model=AdminResponse)
async def update_admin_profile(
        body: AdminUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update admin profile"""
    try:
        # Cập nhật tên admin truyền qua body thay vì params
        if body.name is not None:
            current_admin.name = body.name

        db.commit()
        db.refresh(current_admin)
        
        return AdminResponse(
            id=str(current_admin.id),
            name=current_admin.name,
            email=current_admin.email,
            role=current_admin.role,
            created_at=current_admin.created_at.isoformat() if current_admin.created_at else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
