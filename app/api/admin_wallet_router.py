from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from uuid import UUID

from app.db.database import get_db
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction
from app.models.enums import TransactionType, TransactionStatus
from app.api.auth_router import get_current_user
from app.schemas.wallet import DepositOverviewResponse
from app.schemas.wallet import MessageResponse
from app.services.websocket_manager import manager

router = APIRouter(prefix="/api/admin/wallet", tags=["Admin - Wallet"])


async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user


@router.get("/deposits", response_model=List[dict])
async def list_deposits(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all wallet deposit transactions (admin)."""
    try:
        txs = (
            db.query(WalletTransaction, Wallet, User)
            .join(Wallet, Wallet.id == WalletTransaction.wallet_id)
            .join(User, User.id == Wallet.user_id)
            .filter(WalletTransaction.transaction_type == TransactionType.DEPOSIT)
            .order_by(WalletTransaction.created_at.desc())
            .all()
        )

        result: List[dict] = []
        for tx, wallet, user in txs:
            result.append({
                "id": str(tx.id),
                "user_id": str(user.id),
                "user_email": user.email,
                "amount": float(tx.amount),
                "status": tx.status,
                "bank_name": tx.bank_name,
                "bank_account": tx.bank_account,
                "transfer_code": tx.transfer_code,
                "created_at": tx.created_at.isoformat() if tx.created_at else None
            })

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deposits: {str(e)}"
        )


@router.get("/deposits/overview", response_model=DepositOverviewResponse)
async def get_deposit_overview(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get overview statistics for wallet deposit transactions"""
    try:
        total = db.query(WalletTransaction).filter(WalletTransaction.transaction_type == TransactionType.DEPOSIT).count()
        total_amount = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(WalletTransaction.transaction_type == TransactionType.DEPOSIT).scalar() or 0
        completed = db.query(WalletTransaction).filter(WalletTransaction.transaction_type == TransactionType.DEPOSIT, WalletTransaction.status == "SUCCESS").count()
        pending = db.query(WalletTransaction).filter(WalletTransaction.transaction_type == TransactionType.DEPOSIT, WalletTransaction.status == "PENDING").count()
        rejected = db.query(WalletTransaction).filter(WalletTransaction.transaction_type == TransactionType.DEPOSIT, WalletTransaction.status == "FAILED").count()

        return DepositOverviewResponse(
            total=total,
            total_amount=float(total_amount),
            completed=completed,
            pending=pending,
            rejected=rejected,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deposit overview: {str(e)}"
        )


@router.patch("/deposits/{transaction_id}/reject", response_model=MessageResponse)
async def reject_deposit_transaction(
    transaction_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a pending deposit transaction (admin only)"""
    try:
        tx = db.query(WalletTransaction).filter(
            WalletTransaction.id == transaction_id,
            WalletTransaction.transaction_type == TransactionType.DEPOSIT
        ).first()
        if not tx:
            raise HTTPException(status_code=404, detail="Deposit transaction not found")

        if tx.status != TransactionStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only pending deposits can be rejected")

        # Get wallet and user info
        wallet = db.query(Wallet).filter(Wallet.id == tx.wallet_id).first()
        if wallet:
            tx.status = TransactionStatus.FAILED
            db.commit()
            db.refresh(tx)
            
            # Send WebSocket notification to user with full transaction details
            await manager.send_personal_message({
                "type": "wallet_status_update",
                "event": "deposit_rejected",
                "transaction": {
                    "id": str(tx.id),
                    "status": tx.status,
                    "amount": float(tx.amount),
                    "bank_name": tx.bank_name,
                    "bank_account": tx.bank_account,
                    "transfer_code": tx.transfer_code,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None,
                    "updated_at": tx.updated_at.isoformat() if tx.updated_at else None
                },
                "wallet": {
                    "balance": float(wallet.balance),
                    "total_deposited": float(wallet.total_deposited)
                },
                "message": "Deposit transaction has been rejected",
                "timestamp": tx.updated_at.isoformat() if tx.updated_at else None
            }, str(wallet.user_id))
            
            return MessageResponse(success=True, message="Deposit transaction rejected.")
        else:
            raise HTTPException(status_code=404, detail="Wallet not found")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reject deposit: {str(e)}")




