from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.category import Category
from app.models.workflow import Workflow
from app.models.workflow_category import WorkflowCategory
from typing import List

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_categories(db: Session = Depends(get_db)):
    """Get list of all categories for homepage display"""
    try:
        categories = db.query(Category).all()
        
        result = []
        for category in categories:
            # Count workflows in this category
            workflows_count = db.query(func.count(WorkflowCategory.workflow_id))\
                .filter(WorkflowCategory.category_id == category.id)\
                .scalar() or 0
            
            result.append({
                "id": str(category.id),
                "name": category.name,
                "icon_url": category.image_url,
                "workflows_count": workflows_count
            })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}"
        )
