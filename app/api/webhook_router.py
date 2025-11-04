from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
import logging
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.wallet import Wallet, WalletTransaction
from app.models.enums import TransactionType, TransactionStatus
from app.models.user import User
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhook", tags=["Webhook"])

@router.post("/sepay")
async def sepay_webhook(request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """
    ✅ Sepay Webhook Handler
    - Nhận dữ liệu JSON từ Sepay khi có biến động tài khoản.
    - Log lại payload để kiểm tra.
    - Trả về 200 để Sepay biết webhook đã nhận thành công.
    """
    try:
        payload: Dict[str, Any] = await request.json()
        logger.info("💳 [SEPAY] Webhook payload received: %s", payload)

        # New Sepay JSON format fields
        content: str = str(payload.get("content") or "")
        description: str = str(payload.get("description") or "")
        amount_raw = payload.get("transferAmount")
        if amount_raw is None:
            amount_raw = payload.get("amount") or payload.get("total") or payload.get("money")
        amount: Optional[float] = None
        try:
            amount = float(amount_raw) if amount_raw is not None else None
        except Exception:
            amount = None

        if not content or amount is None:
            logger.warning("[SEPAY] Missing content/amount; ignoring")
            return JSONResponse({"success": True, "message": "Webhook received"})

        # Match rule: find PENDING deposit where tx.transfer_code is substring of content (case-insensitive)
        # and amounts are equal
        candidates = db.query(WalletTransaction).filter(
            WalletTransaction.transaction_type == TransactionType.DEPOSIT,
            WalletTransaction.status == TransactionStatus.PENDING,
            WalletTransaction.amount == amount
        ).all()

        matched: Optional[WalletTransaction] = None
        content_lower = content.lower()
        logger.info("💳 [SEPAY] content: %s", content)
        for c in candidates:
            if c.transfer_code and c.transfer_code.lower() in content_lower:
                matched = c
                break

        if not matched:
            logger.warning("[SEPAY] Unmatched transaction | content=%s amount=%.2f", content, amount or 0)
            return JSONResponse({"success": True, "message": "Webhook received"})

        # Idempotency
        if matched.status == TransactionStatus.SUCCESS:
            logger.info("[SEPAY] Duplicate webhook ignored for transfer=%s", matched.transfer_code)
            return JSONResponse({"success": True, "message": "Webhook received"})

        wallet: Wallet = db.query(Wallet).filter(Wallet.id == matched.wallet_id).first()
        matched.status = TransactionStatus.SUCCESS
        matched.note = f"{matched.note or ''} - Verified via Sepay webhook"
        if wallet:
            wallet.balance += matched.amount
            wallet.total_deposited += matched.amount
        db.commit()

        # Realtime broadcasts
        if wallet:
            await manager.send_personal_message({
                "type": "wallet_update",
                "event": "deposit_success",
                "amount": float(matched.amount),
                "balance": float(wallet.balance)
            }, str(wallet.user_id))

        admins = db.query(User).filter(User.role == "ADMIN").all()
        for admin in admins:
            await manager.send_personal_message({
                "type": "wallet_update",
                "event": "deposit_verified",
                "user_email": None,
                "amount": float(matched.amount)
            }, str(admin.id))

    except Exception as exc:
        raw_body = await request.body()
        logger.exception("❌ [SEPAY] Failed to parse webhook JSON | raw=%s", raw_body[:1000])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {exc}"
        )

    # Sepay chỉ cần nhận HTTP 200 với body JSON bất kỳ
    return JSONResponse({"success": True, "message": "Webhook received"})