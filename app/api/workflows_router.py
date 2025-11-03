from fastapi import APIRouter, HTTPException, Depends, status, Query, Header
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
    WorkflowResponse, WorkflowDetailResponse, WorkflowCreateRequest, WorkflowUpdateRequest,
    CategoryResponse, CategoryCreateRequest, CategoryUpdateRequest,
    ReviewCreateRequest, ReviewResponse
)
from app.schemas.admin import MessageResponse
from app.api.auth_router import get_current_user
from fastapi import HTTPException, status

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        # Decode JWT token manually to avoid exceptions from get_current_user
        import jwt
        from app.core.config import settings
        
        token = credentials.credentials
        
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        return user
        
    except Exception:
        # If any exception occurs, return None
        return None


@router.get("/", response_model=List[WorkflowResponse])
async def get_workflows(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get all published workflows. If authenticated, exclude purchased workflows."""
    try:
        # Base query for active workflows
        query = db.query(Workflow).filter(Workflow.status == "active")
        
        # If user is authenticated, exclude workflows they have purchased
        if current_user:
            # Get purchased workflow IDs
            purchased_workflow_ids = db.query(Purchase.workflow_id)\
                .filter(
                    Purchase.user_id == current_user.id,
                    Purchase.status == "ACTIVE"
                )\
                .subquery()
            
            # Exclude purchased workflows
            query = query.filter(~Workflow.id.in_(purchased_workflow_ids))
        
        workflows = query.options(
            joinedload(Workflow.categories).joinedload(WorkflowCategory.category),
            joinedload(Workflow.assets),
            joinedload(Workflow.favorites)
        ).all()
        
        result = []
        for workflow in workflows:
            categories = [wc.category.name for wc in workflow.categories]
            # Get image URLs from assets (filter by kind="image")
            image_urls = [asset.asset_url for asset in workflow.assets if asset.kind == "image"]
            
            # Check if current user has liked/purchased this workflow (only if authenticated)
            is_like = None
            is_buy = None
            
            if current_user:
                # Check if current user has liked this workflow
                favorite = db.query(Favorite)\
                    .filter(Favorite.workflow_id == workflow.id, Favorite.user_id == current_user.id)\
                    .first()
                is_like = favorite is not None
                
                # Since we filtered out purchased workflows, is_buy should always be false
                is_buy = False
            
            result.append(WorkflowResponse(
                id=str(workflow.id),
                title=workflow.title,
                description=workflow.description,
                price=float(workflow.price),
                status=workflow.status,
                features=workflow.features or [],
                downloads_count=workflow.downloads_count or 0,
                wishlist_count=len(workflow.favorites),
                time_to_setup=workflow.time_to_setup,
                video_demo=workflow.video_demo,
                flow=workflow.flow,
                rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
                created_at=workflow.created_at.isoformat() if workflow.created_at else None,
                updated_at=workflow.updated_at.isoformat() if workflow.updated_at else None,
                categories=categories,
                image_urls=image_urls,
                is_like=is_like,
                is_buy=is_buy
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
    """Get top 10 featured workflows by downloads_count, then by rating_avg."""
    try:
        workflows = db.query(Workflow)\
            .filter(Workflow.status == "active")\
            .order_by(Workflow.downloads_count.desc(), Workflow.rating_avg.desc())\
            .options(
                joinedload(Workflow.categories).joinedload(WorkflowCategory.category),
                joinedload(Workflow.assets),
                joinedload(Workflow.favorites)
            )\
            .limit(10)\
            .all()
        
        result = []
        for workflow in workflows:
            categories = [wc.category.name for wc in workflow.categories]
            # Get image URLs from assets (filter by kind="image")
            image_urls = [asset.asset_url for asset in workflow.assets if asset.kind == "image"]
            
            result.append(WorkflowResponse(
                id=str(workflow.id),
                title=workflow.title,
                description=workflow.description,
                price=float(workflow.price),
                status=workflow.status,
                features=workflow.features or [],
                downloads_count=workflow.downloads_count or 0,
                wishlist_count=len(workflow.favorites),
                time_to_setup=workflow.time_to_setup,
                video_demo=workflow.video_demo,
                flow=workflow.flow,
                rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
                created_at=workflow.created_at.isoformat() if workflow.created_at else None,
                updated_at=workflow.updated_at.isoformat() if workflow.updated_at else None,
                categories=categories,
                image_urls=image_urls,
                is_like=None,
                is_buy=None
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
                "id": str(workflow.id),
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
            .options(
                joinedload(Purchase.workflow).joinedload(Workflow.categories).joinedload(WorkflowCategory.category),
                joinedload(Purchase.workflow).joinedload(Workflow.assets),
                joinedload(Purchase.workflow).joinedload(Workflow.favorites)
            )\
            .all()
        
        result = []
        for purchase in purchases:
            workflow = purchase.workflow
            
            # Get categories and images for the workflow
            categories = [wc.category.name for wc in workflow.categories]
            image_urls = [asset.asset_url for asset in workflow.assets if asset.kind == "image"]
            
            result.append(WorkflowResponse(
                id=str(workflow.id),
                title=workflow.title,
                description=workflow.description,
                price=float(workflow.price),
                status=workflow.status,
                features=workflow.features or [],
                downloads_count=workflow.downloads_count or 0,
                wishlist_count=len(workflow.favorites),
                time_to_setup=workflow.time_to_setup,
                video_demo=workflow.video_demo,
                flow=workflow.flow,
                rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
                created_at=workflow.created_at.isoformat() if workflow.created_at else None,
                updated_at=workflow.updated_at.isoformat() if workflow.updated_at else None,
                categories=categories,
                image_urls=image_urls,
                is_like=None,
                is_buy=None
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user workflows: {str(e)}"
        )


@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow_detail(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
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
        
        # Check if current user has liked/purchased this workflow (only if authenticated)
        is_like = None
        is_buy = None
        
        if current_user:
            # For testing, set to false when user is authenticated
            is_like = False
            is_buy = False
            
            # Check if current user has liked this workflow
            favorite = db.query(Favorite)\
                .filter(Favorite.workflow_id == workflow_id, Favorite.user_id == current_user.id)\
                .first()
            if favorite:
                is_like = True
            
            # Check if current user has purchased this workflow
            purchase = db.query(Purchase)\
                .filter(Purchase.workflow_id == workflow_id, Purchase.user_id == current_user.id)\
                .first()
            if purchase:
                is_buy = True
        
        return WorkflowDetailResponse(
            id=str(workflow.id),
            title=workflow.title,
            description=workflow.description,
            categories=categories,
            image_urls=images,
            features=workflow.features or [],
            rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
            downloads_count=workflow.downloads_count,
            wishlist_count=wishlist_count,
            price=float(workflow.price),
            status=workflow.status,
            time_to_setup=workflow.time_to_setup,
            # video_demo=workflow.video_demo,
            # flow=workflow.flow,
            created_at=workflow.created_at.isoformat() if workflow.created_at else None,
            updated_at=workflow.updated_at.isoformat() if workflow.updated_at else None,
            is_like=is_like,
            is_buy=is_buy
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
            .options(
                joinedload(Workflow.categories).joinedload(WorkflowCategory.category),
                joinedload(Workflow.assets),
                joinedload(Workflow.favorites)
            )\
            .all()
        
        result = []
        for workflow in workflows:
            categories = [wc.category.name for wc in workflow.categories]
            # Get image URLs from assets (filter by kind="image")
            image_urls = [asset.asset_url for asset in workflow.assets if asset.kind == "image"]
            
            result.append(WorkflowResponse(
                id=str(workflow.id),
                title=workflow.title,
                description=workflow.description,
                price=float(workflow.price),
                status=workflow.status,
                features=workflow.features or [],
                downloads_count=workflow.downloads_count or 0,
                wishlist_count=len(workflow.favorites),
                time_to_setup=workflow.time_to_setup,
                video_demo=workflow.video_demo,
                flow=workflow.flow,
                rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
                created_at=workflow.created_at.isoformat() if workflow.created_at else None,
                updated_at=workflow.updated_at.isoformat() if workflow.updated_at else None,
                categories=categories,
                image_urls=image_urls,
                is_like=None,
                is_buy=None
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
    review_data: ReviewCreateRequest,
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
            content=review_data.content
        )
        db.add(review)
        db.commit()
        
        # Update workflow rating average only if rating is provided
        if review_data.rating is not None:
            avg_rating = db.query(func.avg(Comment.rating))\
                .filter(Comment.workflow_id == workflow_id, Comment.rating.isnot(None)).scalar()
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


@router.get("/{workflow_id}/reviews", response_model=List[ReviewResponse])
async def get_workflow_reviews(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get list of reviews for a workflow (with optional authentication)"""
    try:
        reviews = db.query(Comment)\
            .join(User)\
            .filter(Comment.workflow_id == workflow_id)\
            .options(joinedload(Comment.user))\
            .all()
        
        result = []
        for review in reviews:
            # Check if this review belongs to current user
            is_me = current_user is not None and str(review.user_id) == str(current_user.id)
            
            result.append(ReviewResponse(
                id=str(review.id),
                user={
                    "name": review.user.name,
                    "avatar_url": review.user.avatar_url
                },
                rating=review.rating,
                comment=review.content,
                created_at=review.created_at.isoformat(),
                parent_comment_id=str(review.parent_comment_id) if review.parent_comment_id else None,
                is_me=is_me
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflow reviews: {str(e)}"
        )

@router.get("/{workflow_id}/reviews/me", response_model=List[ReviewResponse])
async def get_workflow_reviews_with_auth(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of reviews for a workflow with authentication (shows is_me correctly)"""
    try:
        reviews = db.query(Comment)\
            .join(User)\
            .filter(Comment.workflow_id == workflow_id)\
            .options(joinedload(Comment.user))\
            .all()
        
        result = []
        for review in reviews:
            # Check if this review belongs to current user
            is_me = str(review.user_id) == str(current_user.id)
            
            result.append(ReviewResponse(
                id=str(review.id),
                user={
                    "name": review.user.name,
                    "avatar_url": review.user.avatar_url
                },
                rating=review.rating,
                comment=review.content,
                created_at=review.created_at.isoformat(),
                parent_comment_id=str(review.parent_comment_id) if review.parent_comment_id else None,
                is_me=is_me
            ))
        
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
                joinedload(Workflow.assets),
                joinedload(Workflow.favorites)
            )\
            .filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        categories = [wc.category.name for wc in workflow.categories]
        image_urls = [asset.asset_url for asset in workflow.assets if asset.kind == "image"]
        
        # Check if current user has liked this workflow
        is_like = False
        favorite = db.query(Favorite)\
            .filter(Favorite.workflow_id == workflow_id, Favorite.user_id == current_user.id)\
            .first()
        if favorite:
            is_like = True
        
        # User has purchased, so is_buy should be True
        is_buy = True
        
        return WorkflowResponse(
            id=str(workflow.id),
            title=workflow.title,
            description=workflow.description,
            price=float(workflow.price),
            status=workflow.status,
            features=workflow.features or [],
            downloads_count=workflow.downloads_count or 0,
            wishlist_count=len(workflow.favorites),
            time_to_setup=workflow.time_to_setup,
            video_demo=workflow.video_demo,
            flow=workflow.flow,
            rating_avg=float(workflow.rating_avg) if workflow.rating_avg else None,
            created_at=workflow.created_at.isoformat() if workflow.created_at else None,
            updated_at=workflow.updated_at.isoformat() if workflow.updated_at else None,
            categories=categories,
            image_urls=image_urls,
            is_like=is_like,
            is_buy=is_buy
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflow full detail: {str(e)}"
        )


