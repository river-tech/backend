from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from uuid import UUID
import uuid
import csv
from io import StringIO
from datetime import datetime, date

from app.db.database import get_db
from app.models.user import User
from app.models.purchase import Purchase
from app.models.workflow import Workflow
from app.models.invoice import Invoice
from app.api.auth_router import get_current_user
from app.schemas.purchase import (
    PurchaseOverviewResponse, PurchaseListResponse, PurchaseDetailResponse,
    PurchaseStatusUpdateRequest, PurchaseStatusUpdateResponse
)
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/admin/purchases", tags=["Admin - Purchase Management"])

async def get_current_admin(current_user: User = Depends(get_current_user)):
    """Ensure current user is admin"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

@router.get("/overview", response_model=PurchaseOverviewResponse)
async def get_purchases_overview(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get purchases overview statistics"""
    try:
        # Total purchases
        total_purchases = db.query(Purchase).count()
        
        # Completed purchases
        completed = db.query(Purchase).filter(Purchase.status == "ACTIVE").count()
        
        # Pending purchases
        pending = db.query(Purchase).filter(Purchase.status == "PENDING").count()
        
        # Total revenue
        total_revenue = db.query(func.sum(Workflow.price)).join(
            Purchase, Purchase.workflow_id == Workflow.id
        ).filter(Purchase.status == "ACTIVE").scalar() or 0
        
        return PurchaseOverviewResponse(
            total_purchases=total_purchases,
            completed=completed,
            pending=pending,
            total_revenue=float(total_revenue)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch purchases overview: {str(e)}"
        )

@router.get("/")
async def get_purchases(
    search: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all purchase transactions. If search is provided, filter by user name OR workflow title. No pagination."""
    try:
        # Base query with joins
        query = db.query(Purchase).join(User).join(Workflow)
        
        # Apply filters
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    Workflow.title.ilike(search_term)
                )
            )
        purchases = query.options(
            joinedload(Purchase.user),
            joinedload(Purchase.workflow)
        ).all()
        
        # Build response
        purchases_data = []
        for purchase in purchases:
            purchases_data.append({
                "id": str(purchase.id),
                "user": {
                    "id": str(purchase.user.id),
                    "name": purchase.user.name,
                    "email": purchase.user.email
                },
                "workflow": {
                    "id": str(purchase.workflow.id),
                    "title": purchase.workflow.title,
                    "price": float(purchase.workflow.price)
                },
                "amount": float(purchase.workflow.price),
                "status": purchase.status,
                "payment_method": "WALLET",  # Default for now
                "paid_at": purchase.created_at.isoformat() if purchase.created_at else None
            })
        
        return {"purchases": purchases_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch purchases: {str(e)}"
        )

@router.get("/{purchase_id}", response_model=PurchaseDetailResponse)
async def get_purchase_detail(
    purchase_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get specific purchase transaction details"""
    try:
        purchase = db.query(Purchase).options(
            joinedload(Purchase.user),
            joinedload(Purchase.workflow),
            joinedload(Purchase.invoices)
        ).filter(Purchase.id == purchase_id).first()
        
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase not found"
            )
        
        return PurchaseDetailResponse(
            id=str(purchase.id),
            user={
                "id": str(purchase.user.id),
                "name": purchase.user.name,
                "email": purchase.user.email
            },
            workflow={
                "id": str(purchase.workflow.id),
                "title": purchase.workflow.title,
                "price": float(purchase.workflow.price)
            },
            bank_name=purchase.bank_name,
            transfer_code=purchase.transfer_code,
            status=purchase.status,
            amount=float(purchase.workflow.price),
            paid_at=purchase.created_at.isoformat() if purchase.created_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch purchase detail: {str(e)}"
        )

@router.patch("/{purchase_id}/status", response_model=PurchaseStatusUpdateResponse)
async def update_purchase_status(
    purchase_id: UUID,
    status_data: PurchaseStatusUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update purchase transaction status"""
    try:
        purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase not found"
            )
        
        purchase.status = status_data.status
        db.commit()
        
        return PurchaseStatusUpdateResponse(
            success=True,
            message=f"Purchase status updated to {status_data.status}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update purchase status: {str(e)}"
        )

# @router.get("/export")
# async def export_purchases(
#     format: str = Query("csv"),
#     current_admin: User = Depends(get_current_admin),
#     db: Session = Depends(get_db)
# ):
#     """Export purchases list as CSV"""
#     try:
#         if format.lower() != "csv":
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Only CSV format is supported"
#             )
        
#         # Get all purchases
#         purchases = db.query(Purchase).options(
#             joinedload(Purchase.user),
#             joinedload(Purchase.workflow)
#         ).all()
        
#         # Create CSV content
#         output = StringIO()
#         writer = csv.writer(output)
        
#         # Write header
#         writer.writerow([
#             "Purchase ID", "User Name", "User Email", "Workflow Title",
#             "Amount", "Status", "Payment Method", "Created At"
#         ])
        
#         # Write data
#         for purchase in purchases:
#             writer.writerow([
#                 str(purchase.id),
#                 purchase.user.name,
#                 purchase.user.email,
#                 purchase.workflow.title,
#                 float(purchase.workflow.price),
#                 purchase.status,
#                 "WALLET",
#                 purchase.created_at.isoformat() if purchase.created_at else ""
#             ])
        
#         output.seek(0)
        
#         return StreamingResponse(
#             iter([output.getvalue()]),
#             media_type="text/csv",
#             headers={"Content-Disposition": "attachment; filename=purchases.csv"}
#         )
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to export purchases: {str(e)}"
#         )
