from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session, joinedload
from app.db.database import get_db
from app.models.favorite import Favorite
from app.models.workflow import Workflow
from app.models.workflow_category import WorkflowCategory
from app.models.category import Category
from app.api.auth_router import get_current_user
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of user's favorite workflows"""
    try:
        favorites = db.query(Favorite)\
            .join(Workflow)\
            .filter(Favorite.user_id == current_user.id)\
            .options(joinedload(Favorite.workflow).joinedload(Workflow.categories).joinedload(WorkflowCategory.category))\
            .all()
        
        result = []
        for favorite in favorites:
            workflow = favorite.workflow
            
            # Get categories for this workflow
            categories = []
            for workflow_category in workflow.categories:
                categories.append(workflow_category.category.name)
            
            result.append({
                "id": str(workflow.id),
                "title": workflow.title,
                "price": float(workflow.price),
                "category": categories,
                "date": workflow.created_at.isoformat() if workflow.created_at else None
            })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch wishlist: {str(e)}"
        )
