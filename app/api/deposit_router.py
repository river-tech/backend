from __future__ import annotations

import logging
import os
import random
import string
import uuid
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth_router import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction
from app.models.enums import TransactionType, TransactionStatus
from app.models.notification import Notification
from app.services.websocket_manager import manager


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/wallet", tags=["Wallet - Deposit Init"])


def _generate_transfer_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def _get_or_create_wallet(user_id, db: Session) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(id=uuid.uuid4(), user_id=user_id, balance=0.0, total_deposited=0.0, total_spent=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


class DepositInitRequest(BaseModel):
    amount: float = Field(..., gt=0)
    bank_name: str = Field(..., min_length=1, description="Bank code/name to embed in QR (e.g. MB, MBBank)")


class DepositInitResponse(BaseModel):
    transfer_code: str
    qr_url: str
    transaction_id: str


@router.post("/deposit/init", response_model=DepositInitResponse)
async def init_deposit(
    body: DepositInitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a pending WalletTransaction and return QR URL for Sepay.

    - Generates a unique transfer code server-side
    - Creates WalletTransaction with status=PENDING
    - Builds QR URL from Sepay template and returns to client
    """
    try:
        wallet = _get_or_create_wallet(current_user.id, db)

        # Generate unique transfer code; retry a few times on collision
        transfer_code = _generate_transfer_code(8)
        for _ in range(3):
            exists = db.query(WalletTransaction).filter(
                WalletTransaction.transaction_type == TransactionType.DEPOSIT,
                WalletTransaction.transfer_code == transfer_code
            ).first()
            if not exists:
                break
            transfer_code = _generate_transfer_code(8)

        tx = WalletTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            transaction_type=TransactionType.DEPOSIT,
            amount=body.amount,
            status=TransactionStatus.PENDING,
            bank_name=body.bank_name,
            bank_account=os.getenv("BANK_ACC", "0903536212"),
            transfer_code=transfer_code,
            note=f"Deposit init - transfer: {transfer_code}"
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)

        # Build QR URL using provided bank_name (passed through to 'bank' param)
        qr_url = (
           f"https://qr.sepay.vn/img?acc=VQRQAFCDS7295&bank=MBBank&amount={int(body.amount)}&des={transfer_code}"
        )

        logger.info(
            "[DEPOSIT_INIT] user=%s tx_id=%s amount=%.2f transfer=%s qr=%s",
            current_user.email, tx.id, body.amount, transfer_code, qr_url
        )

        # Create notifications for admins and send realtime message
        admins = db.query(User).filter(User.role == "ADMIN").all()
        created = []
        for admin in admins:
            notif = Notification(
                id=uuid.uuid4(),
                user_id=admin.id,
                title="New deposit request",
                message=f"User {current_user.email} requested a deposit of {int(body.amount):,} VND (code {transfer_code})",
                type="WARNING",
                is_unread=True
            )
            db.add(notif)
            db.flush()
            db.refresh(notif)
            created.append((admin.id, notif))
        db.commit()

        for admin_id, notif in created:
            await manager.send_personal_message({
                "type": "new_deposit_request",
                "event": "deposit_created",
                "transaction": {
                    "id": str(tx.id),
                    "status": tx.status,
                    "amount": float(tx.amount),
                    "bank_name": tx.bank_name,
                    "bank_account": tx.bank_account,
                    "transfer_code": tx.transfer_code,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None
                },
                "user": {
                    "id": str(current_user.id),
                    "name": current_user.name,
                    "email": current_user.email
                },
                "notification": {
                    "id": str(notif.id),
                    "title": notif.title,
                    "message": notif.message,
                    "type": notif.type,
                    "is_unread": notif.is_unread,
                    "created_at": notif.created_at.isoformat() if notif.created_at else None
                },
                "message": f"User {current_user.name or current_user.email} suggested a new deposit request",
                "timestamp": tx.created_at.isoformat() if tx.created_at else None
            }, str(admin_id))

        return DepositInitResponse(
            transfer_code=transfer_code,
            qr_url=qr_url,
            transaction_id=str(tx.id)
        )
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("[DEPOSIT_INIT] Failed to init deposit")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


