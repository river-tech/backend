from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from uuid import UUID
import uuid

from app.db.database import get_db
from app.models.user import User
from app.models.workflow import Workflow
from app.models.workflow_asset import WorkflowAsset
from app.models.workflow_category import WorkflowCategory
from app.models.category import Category
from app.models.purchase import Purchase
from app.schemas.workflow import (
    AdminWorkflowListResponse,
    AdminWorkflowListRequest,
    AdminWorkflowOverviewResponse,
    AdminWorkflowDetailResponse,
    AdminWorkflowCreateRequest,
    AdminWorkflowCreateResponse,
    AdminWorkflowUpdateRequest,
    AdminWorkflowUpdateResponse,
    AdminWorkflowDeleteResponse,
    AdminWorkflowAssetUploadRequest,
    AdminWorkflowAssetUploadResponse,
    AdminWorkflowAssetDeleteResponse
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

router = APIRouter(prefix="/api/admin/workflows", tags=["Admin - Workflow Management"])

@router.get("/", response_model=List[AdminWorkflowListResponse])
async def list_all_workflows(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Return all workflows (no pagination), with basic stats for admin table."""
    try:
        workflows = db.query(Workflow).all()

        results: List[AdminWorkflowListResponse] = []
        for wf in workflows:
            # Sales count from ACTIVE purchases
            sales_count = db.query(Purchase).filter(
                Purchase.workflow_id == wf.id,
                Purchase.status == "ACTIVE"
            ).count()

            # Categories as names list
            category_names: List[str] = []
            for wc in wf.categories:
                if wc.category and wc.category.name:
                    category_names.append(wc.category.name)

            results.append(AdminWorkflowListResponse(
                id=str(wf.id),
                title=wf.title,
                categories=category_names,
                price=float(wf.price),
                sales_count=sales_count,
                created_at=wf.created_at.isoformat() if getattr(wf, 'created_at', None) else "",
                status=wf.status
            ))

        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflows: {str(e)}"
        )

@router.get("/overview", response_model=AdminWorkflowOverviewResponse)
async def get_workflows_overview(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get workflows overview"""
    try:
        # Total workflows
        total_workflows = db.query(Workflow).count()
        
        # Active workflows
        active_workflows = db.query(Workflow).filter(Workflow.status == "active").count()
        
        # Total sales
        total_sales = db.query(Purchase).filter(Purchase.status == "ACTIVE").count()
        
        # Total revenue
        total_revenue_result = db.query(func.sum(Workflow.price)).join(
            Purchase, Workflow.id == Purchase.workflow_id
        ).filter(Purchase.status == "ACTIVE").scalar()
        
        total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
        
        return AdminWorkflowOverviewResponse(
            total_workflows=total_workflows,
            active_workflows=active_workflows,
            total_sales=total_sales,
            total_revenue=total_revenue
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflows overview: {str(e)}"
        )

@router.get("/{workflow_id}", response_model=AdminWorkflowDetailResponse)
async def get_workflow_detail(
    workflow_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get workflow detail"""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Get categories
        categories = []
        for wc in workflow.categories:
            categories.append({
                "id": str(wc.category.id),
                "name": wc.category.name
            })
        
        # Build assets list: images only with id and url
        image_assets: List[dict] = [
            {"id": str(a.id), "url": a.asset_url} for a in workflow.assets if a.kind == "image"
        ]
        # Ensure only one video: prefer workflow.video_demo; otherwise, pick the first video asset
        if not workflow.video_demo:
            first_video = next((a.asset_url for a in workflow.assets if a.kind == "video"), None)
            video_demo_url = first_video
        else:
            video_demo_url = workflow.video_demo

        # Sales count
        sales_count = db.query(Purchase).filter(
            Purchase.workflow_id == workflow.id,
            Purchase.status == "ACTIVE"
        ).count()

        return AdminWorkflowDetailResponse(
            id=str(workflow.id),
            title=workflow.title,
            description=workflow.description,
            price=float(workflow.price),
            rating=float(workflow.rating_avg) if getattr(workflow, "rating_avg", None) else None,
            features=workflow.features or [],
            time_to_setup=workflow.time_to_setup,
            video_demo=video_demo_url,
            flow=workflow.flow,
            status=workflow.status,
            created_at=workflow.created_at.isoformat() if getattr(workflow, "created_at", None) else None,
            sales_count=sales_count,
            categories=categories,
            assets=image_assets
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow detail: {str(e)}"
        )

@router.post("/create", response_model=AdminWorkflowCreateResponse)
async def create_workflow(
    request: AdminWorkflowCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new workflow with JSON body"""
    try:
        # Flow is already a JSON object
        flow_data = request.flow
        
        # Create workflow
        workflow = Workflow(
            id=uuid.uuid4(),
            title=request.title,
            description=request.description,
            price=request.price,
            features=request.features,
            time_to_setup=request.time_to_setup,
            video_demo=request.video_demo,
            flow=flow_data,
            status="active",
            downloads_count=0
        )
        
        db.add(workflow)
        db.flush()  # Get the ID
        
        # Add categories
        for category_id in request.category_ids:
            category = db.query(Category).filter(Category.id == category_id).first()
            if category:
                workflow_category = WorkflowCategory(
                    id=uuid.uuid4(),
                    workflow_id=workflow.id,
                    category_id=category.id
                )
                db.add(workflow_category)
        
        # Auto-create video asset if video_demo is provided
        if request.video_demo:
            video_asset = WorkflowAsset(
                id=uuid.uuid4(),
                workflow_id=workflow.id,
                kind="video",
                asset_url=request.video_demo
            )
            db.add(video_asset)
        
        db.commit()
        db.refresh(workflow)
        
        return AdminWorkflowCreateResponse(
            id=str(workflow.id),
            title=workflow.title,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )

# @router.post("/create-with-file", response_model=AdminWorkflowCreateResponse)
# async def create_workflow_with_file(
#     title: str = Form(...),
#     description: str = Form(...),
#     price: float = Form(...),
#     features: str = Form("[]"),  # JSON string
#     time_to_setup: Optional[int] = Form(None),
#     video_demo: Optional[str] = Form(None),
#     flow_file: Optional[UploadFile] = File(None),  # JSON file upload
#     category_ids: str = Form("[]"),  # JSON string
#     current_admin: User = Depends(get_current_admin),
#     db: Session = Depends(get_db)
# ):
#     """Create a new workflow with file upload for flow"""
#     try:
#         import json
        
#         # Parse features from JSON string
#         try:
#             features_list = json.loads(features) if features else []
#         except json.JSONDecodeError:
#             features_list = []
        
#         # Parse category_ids from JSON string
#         try:
#             category_ids_list = json.loads(category_ids) if category_ids else []
#         except json.JSONDecodeError:
#             category_ids_list = []
        
#         # Parse flow from uploaded JSON file
#         flow_data = None
#         if flow_file and flow_file.filename:
#             try:
#                 content = await flow_file.read()
#                 flow_data = json.loads(content.decode('utf-8'))
#             except (json.JSONDecodeError, UnicodeDecodeError) as e:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Invalid JSON file for flow: {str(e)}"
#                 )
        
#         # Create workflow
#         workflow = Workflow(
#             id=uuid.uuid4(),
#             title=title,
#             description=description,
#             price=price,
#             features=features_list,
#             time_to_setup=time_to_setup,
#             video_demo=video_demo,
#             flow=flow_data,
#             status="active",
#             downloads_count=0
#         )
        
#         db.add(workflow)
#         db.flush()  # Get the ID
        
#         # Add categories
#         for category_id in category_ids_list:
#             category = db.query(Category).filter(Category.id == category_id).first()
#             if category:
#                 workflow_category = WorkflowCategory(
#                     id=uuid.uuid4(),
#                     workflow_id=workflow.id,
#                     category_id=category.id
#                 )
#                 db.add(workflow_category)
        
#         # Auto-create video asset if video_demo is provided
#         if video_demo:
#             video_asset = WorkflowAsset(
#                 id=uuid.uuid4(),
#                 workflow_id=workflow.id,
#                 kind="video",
#                 asset_url=video_demo
#             )
#             db.add(video_asset)
        
#         db.commit()
#         db.refresh(workflow)
        
#         return AdminWorkflowCreateResponse(
#             id=str(workflow.id),
#             title=workflow.title,
#             success=True
#         )
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to create workflow: {str(e)}"
#         )

@router.put("/{workflow_id}", response_model=AdminWorkflowUpdateResponse)
async def update_workflow(
    workflow_id: UUID,
    request: AdminWorkflowUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update workflow information"""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Update fields
        if request.title is not None:
            workflow.title = request.title
        if request.description is not None:
            workflow.description = request.description
        if request.price is not None:
            workflow.price = request.price
        if request.features is not None:
            workflow.features = request.features
        if request.time_to_setup is not None:
            workflow.time_to_setup = request.time_to_setup
        if request.video_demo is not None:
            workflow.video_demo = request.video_demo
        if request.flow is not None:
            workflow.flow = request.flow
        
        # Update categories if provided
        if request.category_ids is not None:
            # Remove existing categories
            db.query(WorkflowCategory).filter(
                WorkflowCategory.workflow_id == workflow_id
            ).delete()

            # Validate and add new categories (skip invalid UUIDs)
            valid_category_ids = []
            for raw_category_id in request.category_ids:
                try:
                    cid = UUID(str(raw_category_id))
                    valid_category_ids.append(cid)
                except Exception:
                    # skip invalid UUID strings like "string"
                    continue

            for cid in valid_category_ids:
                category = db.query(Category).filter(Category.id == cid).first()
                if category:
                    workflow_category = WorkflowCategory(
                        id=uuid.uuid4(),
                        workflow_id=workflow.id,
                        category_id=category.id
                    )
                    db.add(workflow_category)
        
        db.commit()
        
        return AdminWorkflowUpdateResponse(
            success=True,
            message="Workflow updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}"
        )

@router.delete("/{workflow_id}", response_model=AdminWorkflowDeleteResponse)
async def deactivate_workflow(
    workflow_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Deactivate workflow (soft delete)"""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Deactivate workflow
        workflow.status = "inactive"
        db.commit()
        
        return AdminWorkflowDeleteResponse(
            success=True,
            message="Workflow deactivated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate workflow: {str(e)}"
        )

@router.patch("/{workflow_id}/activate", response_model=AdminWorkflowDeleteResponse)
async def activate_workflow(
    workflow_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate workflow"""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Activate workflow
        workflow.status = "active"
        db.commit()
        
        return AdminWorkflowDeleteResponse(
            success=True,
            message="Workflow activated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate workflow: {str(e)}"
        )

@router.post("/{workflow_id}/assets", response_model=AdminWorkflowAssetUploadResponse)
async def upload_workflow_asset(
    workflow_id: UUID,
    request: AdminWorkflowAssetUploadRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Upload asset (image, file, video) for workflow"""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        asset = WorkflowAsset(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            kind=request.kind,
            asset_url=request.asset_url
        )
        
        db.add(asset)
        db.commit()
        db.refresh(asset)
        
        return AdminWorkflowAssetUploadResponse(
            success=True,
            asset_id=str(asset.id),
            asset_url=asset.asset_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload asset: {str(e)}"
        )

@router.delete("/{workflow_id}/assets/{asset_id}", response_model=AdminWorkflowAssetDeleteResponse)
async def delete_workflow_asset(
    workflow_id: UUID,
    asset_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete asset from workflow"""
    try:
        asset = db.query(WorkflowAsset).filter(
            WorkflowAsset.id == asset_id,
            WorkflowAsset.workflow_id == workflow_id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        db.delete(asset)
        db.commit()
        
        return AdminWorkflowAssetDeleteResponse(success=True)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete asset: {str(e)}"
        )