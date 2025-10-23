from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session, joinedload
from app.db.database import get_db
from app.models.purchase import Purchase
from app.models.invoice import Invoice
from app.models.workflow import Workflow
from app.models.workflow_category import WorkflowCategory
from app.models.category import Category
from app.api.auth_router import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

router = APIRouter()

class OrderCreateRequest(BaseModel):
    bank_account: str
    bank_name: str
    transfer_code: str

class OrderResponse(BaseModel):
    success: bool
    message: str
    order: dict

class InvoiceResponse(BaseModel):
    invoice_number: str
    issued_at: datetime
    status: str
    billing_name: str
    billing_email: str
    workflow: dict
    amount: float


# Lấy hóa đơn chi tiết theo workflow_id (nếu user đã mua workflow đó)
@router.get("/workflow/{workflow_id}/invoice", response_model=InvoiceResponse)
async def get_invoice_by_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice for a workflow the user has purchased"""
    try:
        purchase = db.query(Purchase)\
            .join(Invoice)\
            .filter(
                Purchase.workflow_id == workflow_id,
                Purchase.user_id == current_user.id,
                Purchase.status == "ACTIVE"
            )\
            .options(joinedload(Purchase.workflow).joinedload(Workflow.categories).joinedload(WorkflowCategory.category))\
            .first()
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        invoice = purchase.invoices[0] if purchase.invoices else None
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        categories = [wc.category.name for wc in purchase.workflow.categories]
        return InvoiceResponse(
            invoice_number=str(invoice.id),
            issued_at=invoice.issued_at,
            status=purchase.status,
            billing_name=invoice.billing_name,
            billing_email=invoice.billing_email,
            workflow={
                "id": str(purchase.workflow.id),
                "title": purchase.workflow.title,
                "category": categories,
                "price": float(purchase.workflow.price)
            },
            amount=float(invoice.amount)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invoice: {str(e)}"
        )

# Lấy hóa đơn chi tiết theo purchase_id
@router.get("/{purchase_id}/invoice", response_model=InvoiceResponse)
async def get_invoice_by_purchase(
    purchase_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice for a specific purchase"""
    try:
        purchase = db.query(Purchase)\
            .join(Invoice)\
            .filter(
                Purchase.id == purchase_id,
                Purchase.user_id == current_user.id,
                Purchase.status == "ACTIVE"
            )\
            .options(joinedload(Purchase.workflow).joinedload(Workflow.categories).joinedload(WorkflowCategory.category))\
            .first()
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        invoice = purchase.invoices[0] if purchase.invoices else None
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        categories = [wc.category.name for wc in purchase.workflow.categories]
        return InvoiceResponse(
            invoice_number=str(invoice.id),
            issued_at=invoice.issued_at,
            status=purchase.status,
            billing_name=invoice.billing_name,
            billing_email=invoice.billing_email,
            workflow={
                "id": str(purchase.workflow.id),
                "title": purchase.workflow.title,
                "category": categories,
                "price": float(purchase.workflow.price)
            },
            amount=float(invoice.amount)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invoice: {str(e)}"
        )

@router.post("/{workflow_id}", response_model=OrderResponse)
async def create_order(
    workflow_id: UUID,
    order_data: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order for purchasing a workflow"""
    try:
        # Check if workflow exists
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Check if user already purchased this workflow
        existing_purchase = db.query(Purchase).filter(
            Purchase.user_id == current_user.id,
            Purchase.workflow_id == workflow_id,
            Purchase.status == "ACTIVE"
        ).first()
        
        if existing_purchase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already purchased this workflow"
            )
        
        # Create purchase
        import uuid
        purchase = Purchase(
            id=uuid.uuid4(),
            user_id=current_user.id,
            workflow_id=workflow_id,
            bank_account=order_data.bank_account,
            bank_name=order_data.bank_name,
            transfer_code=order_data.transfer_code,
            amount=workflow.price,
            status="PENDING",
            payment_method="QR",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        
        return OrderResponse(
            success=True,
            message="Order created successfully",
            order={
                "id": str(purchase.id),
                "workflow_id": str(workflow_id),
                "transfer_code": purchase.transfer_code,
                "bank_name": purchase.bank_name,
                "account_number": purchase.bank_account,
                "amount": float(purchase.amount),
                "status": purchase.status,
                "created_at": purchase.created_at.isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )
