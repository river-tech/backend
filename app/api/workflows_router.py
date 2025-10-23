from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.models import (
    Workflow, Category, WorkflowCategory, WorkflowAsset, 
    Favorite, Comment, Purchase, Invoice, User
)
from app.schemas.workflow import (
    WorkflowResponse, WorkflowCreateRequest, WorkflowUpdateRequest,
    CategoryResponse, CategoryCreateRequest, CategoryUpdateRequest
)
from app.schemas.admin import MessageResponse
from app.api.auth_router import get_current_user

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


@router.get("/", response_model=List[WorkflowResponse])
async def get_workflows(
    db: Session = Depends(get_db)
):
    """Get all published workflows (no query params)."""
    try:
        workflows = (
            db.query(Workflow)
            .filter(Workflow.status == "active")
            .options(joinedload(Workflow.categories).joinedload(WorkflowCategory.category))
            .all()
        )
        
        result = []
        for workflow in workflows:
            categories = [wc.category.name for wc in workflow.categories]
            result.append(WorkflowResponse(
                id=workflow.id,
                title=workflow.title,
                description=workflow.description,
                category=categories,
                features=workflow.features or [],
                rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
                downloads_count=workflow.downloads_count,
                price=float(workflow.price)
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflows: {str(e)}"
        )


@router.get("/feature", response_model=List[WorkflowResponse])
async def get_featured_workflows(
    db: Session = Depends(get_db)
):
    """Get all featured workflows (rating >= 4.0). No query params."""
    try:
        workflows = db.query(Workflow)\
            .filter(Workflow.status == "active")\
            .filter(Workflow.rating_avg >= 4.0)\
            .order_by(Workflow.downloads_count.desc())\
            .options(joinedload(Workflow.categories).joinedload(WorkflowCategory.category))\
            .all()
        
        result = []
        for workflow in workflows:
            categories = [wc.category.name for wc in workflow.categories]
            result.append(WorkflowResponse(
                id=workflow.id,
                title=workflow.title,
                description=workflow.description,
                category=categories,
                features=workflow.features or [],
                rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
                downloads_count=workflow.downloads_count,
                price=float(workflow.price)
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch featured workflows: {str(e)}"
        )


@router.get("/{workflow_id}/related", response_model=List[dict])
async def get_related_workflows(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Get 3 related workflows from the same categories"""
    try:
        # Get workflow categories
        workflow_categories = db.query(WorkflowCategory.category_id)\
            .filter(WorkflowCategory.workflow_id == workflow_id).all()
        
        if not workflow_categories:
            return []
        
        category_ids = [wc.category_id for wc in workflow_categories]
        
        # Get related workflows
        related_workflows = db.query(Workflow)\
            .join(WorkflowCategory)\
            .filter(
                and_(
                    Workflow.id != workflow_id,
                    Workflow.status == "active",
                    WorkflowCategory.category_id.in_(category_ids)
                )
            )\
            .options(joinedload(Workflow.assets))\
            .limit(3).all()
        
        result = []
        for workflow in related_workflows:
            thumbnail_url = None
            if workflow.assets:
                image_assets = [asset for asset in workflow.assets if asset.kind == "image"]
                if image_assets:
                    thumbnail_url = image_assets[0].asset_url
            
            result.append({
                "id": workflow.id,
                "title": workflow.title,
                "thumbnail_url": thumbnail_url,
                "rating_avg": float(workflow.rating_avg) if workflow.rating_avg else None,
                "price": float(workflow.price)
            })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch related workflows: {str(e)}"
        )


@router.get("/my-workflow", response_model=List[WorkflowResponse])
async def get_my_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of workflows that user has purchased"""
    try:
        purchases = db.query(Purchase)\
            .join(Workflow)\
            .filter(
                and_(
                    Purchase.user_id == current_user.id,
                    Purchase.status == "ACTIVE"
                )
            )\
            .options(joinedload(Purchase.workflow))\
            .all()
        
        result = []
        for purchase in purchases:
            result.append(WorkflowResponse(
                id=purchase.id,
                workflow={
                    "id": purchase.workflow.id,
                    "title": purchase.workflow.title
                },
                purchase_date=purchase.paid_at or purchase.created_at,
                price=float(purchase.amount),
                status="Active" if purchase.status == "ACTIVE" else "Expired"
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user workflows: {str(e)}"
        )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_detail(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information of a workflow"""
    try:
        workflow = db.query(Workflow)\
            .options(
                joinedload(Workflow.categories).joinedload(WorkflowCategory.category),
                joinedload(Workflow.assets),
                joinedload(Workflow.favorites),
                joinedload(Workflow.comments)
            )\
            .filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        categories = [wc.category.name for wc in workflow.categories]
        images = [asset.asset_url for asset in workflow.assets if asset.kind == "image"]
        
        # Count ratings and wishlist
        rating_count = db.query(func.count(Comment.id))\
            .filter(Comment.workflow_id == workflow_id).scalar() or 0
        
        wishlist_count = db.query(func.count(Favorite.id))\
            .filter(Favorite.workflow_id == workflow_id).scalar() or 0
        
        return WorkflowResponse(
            id=workflow.id,
            title=workflow.title,
            description=workflow.description,
            category=categories,
            images=images,
            features=workflow.features or [],
            rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
            rating_count=rating_count,
            downloads_count=workflow.downloads_count,
            wishlist_count=wishlist_count,
            price=float(workflow.price),
            time_to_setup=workflow.time_to_setup
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflow detail: {str(e)}"
        )


@router.get("/search", response_model=List[WorkflowResponse])
async def search_workflows(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Search workflows by keyword (no pagination params)."""
    try:
        search_term = f"%{q}%"
        workflows = db.query(Workflow)\
            .filter(
                and_(
                    Workflow.status == "active",
                    or_(
                        Workflow.title.ilike(search_term),
                        Workflow.description.ilike(search_term)
                    )
                )
            )\
            .options(joinedload(Workflow.categories).joinedload(WorkflowCategory.category))\
            .all()
        
        result = []
        for workflow in workflows:
            categories = [wc.category.name for wc in workflow.categories]
            result.append(WorkflowResponse(
                id=workflow.id,
                title=workflow.title,
                description=workflow.description,
                category=categories,
                features=workflow.features or [],
                rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
                downloads_count=workflow.downloads_count,
                price=float(workflow.price)
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search workflows: {str(e)}"
        )


@router.post("/{workflow_id}/wishlist", response_model=MessageResponse)
async def add_to_wishlist(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add workflow to wishlist"""
    try:
        # Check if workflow exists
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Check if already in wishlist
        existing_favorite = db.query(Favorite)\
            .filter(
                and_(
                    Favorite.user_id == current_user.id,
                    Favorite.workflow_id == workflow_id
                )
            ).first()
        
        if existing_favorite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow already in wishlist"
            )
        
        # Add to wishlist
        favorite = Favorite(
            user_id=current_user.id,
            workflow_id=workflow_id
        )
        db.add(favorite)
        db.commit()
        
        return MessageResponse(success=True, message="Added to wishlist")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add to wishlist: {str(e)}"
        )


@router.delete("/{workflow_id}/wishlist", response_model=MessageResponse)
async def remove_from_wishlist(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove workflow from wishlist"""
    try:
        favorite = db.query(Favorite)\
            .filter(
                and_(
                    Favorite.user_id == current_user.id,
                    Favorite.workflow_id == workflow_id
                )
            ).first()
        
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not in wishlist"
            )
        
        db.delete(favorite)
        db.commit()
        
        return MessageResponse(success=True, message="Removed from wishlist")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove from wishlist: {str(e)}"
        )


@router.post("/{workflow_id}/reviews", response_model=MessageResponse)
async def create_review(
    workflow_id: UUID,
    review_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new review for workflow"""
    try:
        # Check if workflow exists
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Create review
        review = Comment(
            workflow_id=workflow_id,
            user_id=current_user.id,
            rating=review_data.rating,
            parent_comment_id=review_data.parent_comment_id,
            content=review_data.comment
        )
        db.add(review)
        db.commit()
        
        # Update workflow rating average
        avg_rating = db.query(func.avg(Comment.rating))\
            .filter(Comment.workflow_id == workflow_id).scalar()
        workflow.rating_avg = avg_rating
        db.commit()
        
        return MessageResponse(success=True, message="Review added successfully")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )


@router.delete("/reviews/{review_id}", response_model=MessageResponse)
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review or comment"""
    try:
        review = db.query(Comment)\
            .filter(
                and_(
                    Comment.id == review_id,
                    Comment.user_id == current_user.id
                )
            ).first()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        workflow_id = review.workflow_id
        db.delete(review)
        db.commit()
        
        # Update workflow rating average
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if workflow:
            avg_rating = db.query(func.avg(Comment.rating))\
                .filter(Comment.workflow_id == workflow_id).scalar()
            workflow.rating_avg = avg_rating
            db.commit()
        
        return MessageResponse(success=True, message="Review deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete review: {str(e)}"
        )


@router.get("/{workflow_id}/reviews", response_model=List[WorkflowResponse])
async def get_workflow_reviews(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Get list of reviews for a workflow"""
    try:
        reviews = db.query(Comment)\
            .join(User)\
            .filter(Comment.workflow_id == workflow_id)\
            .options(joinedload(Comment.user))\
            .all()
        
        result = []
        for review in reviews:
            result.append({
                "id": str(review.id),
                "user": {
                    "name": review.user.name,
                    "avatar_url": review.user.avatar_url
                },
                "rating": review.rating,
                "comment": review.content,
                "created_at": review.created_at,
                "parent_comment_id": str(review.parent_comment_id) if review.parent_comment_id else None
            })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflow reviews: {str(e)}"
        )


@router.get("/detail/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_full_detail(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full details of a workflow (including video tutorial, download files, setup guide...)"""
    try:
        # Check if user purchased this workflow
        purchase = db.query(Purchase)\
            .filter(
                and_(
                    Purchase.user_id == current_user.id,
                    Purchase.workflow_id == workflow_id,
                    Purchase.status == "ACTIVE"
                )
            ).first()
        
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must purchase this workflow to access full details"
            )
        
        workflow = db.query(Workflow)\
            .options(
                joinedload(Workflow.categories).joinedload(WorkflowCategory.category),
                joinedload(Workflow.assets)
            )\
            .filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        categories = [wc.category.name for wc in workflow.categories]
        document_assets = [asset.asset_url for asset in workflow.assets if asset.kind == "doc"]
        
        return WorkflowResponse(
            id=workflow.id,
            title=workflow.title,
            category=categories,
            status=workflow.status,
            purchased_at=purchase.paid_at,
            video_demo_url=workflow.video_demo,
            last_updated=workflow.updated_at,
            document=document_assets[0] if document_assets else None,
            flow=workflow.flow
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflow full detail: {str(e)}"
        )


