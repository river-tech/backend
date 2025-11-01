from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.models.user import User
from app.models.category import Category
from app.api.auth_router import get_current_user

class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    image_url: str | None = None

class CategoryCreateResponse(BaseModel):
    id: str
    name: str
    success: bool

router = APIRouter(prefix="/api/admin/categories", tags=["Admin - Categories"])

async def get_current_admin(current_user: User = Depends(get_current_user)):
    """Ensure current user is admin"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

@router.get("/")
async def get_categories(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all workflow categories"""
    try:
        categories = db.query(Category).all()
        
        categories_data = []
        for category in categories:
            categories_data.append({
                "id": str(category.id),
                "name": category.name,
                "image_url": category.image_url
            })
        
        return categories_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}"
        )

@router.post("/", response_model=CategoryCreateResponse)
async def create_category(
    request: CategoryCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new workflow category"""
    try:
        # Check if category name already exists
        existing_category = db.query(Category).filter(
            Category.name.ilike(request.name.strip())
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        # Create new category
        category = Category(
            id=uuid.uuid4(),
            name=request.name.strip(),
            image_url=request.image_url.strip() if request.image_url else None
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        return CategoryCreateResponse(
            id=str(category.id),
            name=category.name,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}"
        )

@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a workflow category from system"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check if category is being used by any workflows
        from app.models.workflow_category import WorkflowCategory
        workflow_count = db.query(WorkflowCategory).filter(
            WorkflowCategory.category_id == category_id
        ).count()
        
        if workflow_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category. It is being used by {workflow_count} workflow(s)"
            )
        
        db.delete(category)
        db.commit()
        
        return {
            "success": True,
            "message": "Category deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}"
        )
