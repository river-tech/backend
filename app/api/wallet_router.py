from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction
from app.models.purchase import Purchase
from app.models.workflow import Workflow
from app.models.notification import Notification
from app.models.enums import TransactionType, TransactionStatus
from app.api.auth_router import get_current_user
from app.services.websocket_manager import manager
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import uuid

router = APIRouter()

# Import schemas from schemas module
from app.schemas.wallet import (
    WalletResponse, WalletTransactionResponse, DepositRequest, DepositResponse,
    PurchaseWithWalletRequest, PurchaseWithWalletResponse, LastBankInfoResponse,
    AdminActivateDepositRequest, AdminActivateDepositResponse
)

# Helper function to get or create wallet
def get_or_create_wallet(user_id: UUID, db: Session) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(
            id=uuid.uuid4(),
            user_id=user_id,
            balance=0.0,
            total_deposited=0.0,
            total_spent=0.0
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

# 33. GET /api/wallet - Lấy thông tin ví của người dùng hiện tại
@router.get("/", response_model=WalletResponse)
async def get_wallet_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin ví của người dùng hiện tại (số dư, tổng nạp, tổng đã tiêu)"""
    try:
        wallet = get_or_create_wallet(current_user.id, db)
        
        return WalletResponse(
            balance=float(wallet.balance),
            total_deposited=float(wallet.total_deposited),
            total_spent=float(wallet.total_spent)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch wallet info: {str(e)}"
        )

# 34. GET /api/wallet/transactions - Lấy lịch sử giao dịch ví của người dùng
@router.get("/transactions", response_model=List[WalletTransactionResponse])
async def get_wallet_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử giao dịch ví của người dùng"""
    try:
        wallet = get_or_create_wallet(current_user.id, db)
        
        # Get all transactions
        transactions = db.query(WalletTransaction)\
            .filter(WalletTransaction.wallet_id == wallet.id)\
            .order_by(WalletTransaction.created_at.desc())\
            .all()
        
        return [
            WalletTransactionResponse(
                id=tx.id,
                transaction_type=tx.transaction_type,
                amount=float(tx.amount),
                status=tx.status,
                bank_name=tx.bank_name,
                bank_account=tx.bank_account,
                transfer_code=tx.transfer_code,
                note=tx.note,
                created_at=tx.created_at
            )
            for tx in transactions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch wallet transactions: {str(e)}"
        )

# 36. GET /api/wallet/last-bank-info - Lấy thông tin ngân hàng + số tài khoản của lần nạp tiền thành công gần nhất
@router.get("/last-bank-info", response_model=dict)
async def get_last_bank_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin ngân hàng + số tài khoản của lần nạp tiền gần nhất"""
    try:
        wallet = get_or_create_wallet(current_user.id, db)
        
        # Tìm transaction DEPOSIT gần nhất (không cần thành công)
        last_deposit = db.query(WalletTransaction)\
            .filter(
                WalletTransaction.wallet_id == wallet.id,
                WalletTransaction.transaction_type == TransactionType.DEPOSIT,
                WalletTransaction.bank_name.isnot(None)
            )\
            .order_by(WalletTransaction.created_at.desc())\
            .first()
        
        if not last_deposit:
            return {
                "bank_name": None,
                "bank_account": None
            }
        
        return {
            "bank_name": last_deposit.bank_name,
            "bank_account": last_deposit.bank_account
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch last bank info: {str(e)}"
        )

# 35. POST /api/wallet/deposit - Tạo yêu cầu nạp tiền vào ví
@router.post("/deposit", response_model=DepositResponse)
async def create_deposit_request(
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo yêu cầu nạp tiền vào ví (qua QR banking)"""
    try:
        wallet = get_or_create_wallet(current_user.id, db)
        
        # Check if transfer_code already exists
        existing_tx = db.query(WalletTransaction).filter(
            WalletTransaction.note.like(f"%{deposit_data.transfer_code}%"),
            WalletTransaction.transaction_type == TransactionType.DEPOSIT
        ).first()
        
        if existing_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer code already exists"
            )
        
        # Create deposit transaction
        transaction = WalletTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            transaction_type=TransactionType.DEPOSIT,
            amount=deposit_data.amount,
            status=TransactionStatus.PENDING,
            bank_name=deposit_data.bank_name,
            bank_account=deposit_data.bank_account,
            transfer_code=deposit_data.transfer_code,
            note=f"Deposit request via {deposit_data.bank_name} - Transfer code: {deposit_data.transfer_code}"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Get user info for notification
        user = db.query(User).filter(User.id == current_user.id).first()
        
        # Create notification and send WebSocket message to all admins
        admins = db.query(User).filter(User.role == "ADMIN").all()
        
        notifications_list = []
        for admin in admins:
            # Create notification for admin
            notification = Notification(
                id=uuid.uuid4(),
                user_id=admin.id,
                title="New deposit request",
                message=f"User {user.email} suggested a new deposit request of {deposit_data.amount:,.0f} VNĐ",
                type="WARNING",
                is_unread=True
            )
            db.add(notification)
            db.flush()  # Flush to get notification.id
            db.refresh(notification)
            notifications_list.append((notification, admin.id))
        
        db.commit()
        
        # Send WebSocket messages after commit
        for notification, admin_id in notifications_list:
            await manager.send_personal_message({
                "type": "new_deposit_request",
                "event": "deposit_created",
                "transaction": {
                    "id": str(transaction.id),
                    "status": transaction.status,
                    "amount": float(transaction.amount),
                    "bank_name": transaction.bank_name,
                    "bank_account": transaction.bank_account,
                    "transfer_code": transaction.transfer_code,
                    "created_at": transaction.created_at.isoformat() if transaction.created_at else None
                },
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email
                },
                "notification": {
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type,
                    "is_unread": notification.is_unread,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None
                },
                "message": f"User {user.name} suggested a new deposit request",
                "timestamp": transaction.created_at.isoformat() if transaction.created_at else None
            }, str(admin_id))
        
        return DepositResponse(
            success=True,
            message="Deposit request created",
            transaction_id=transaction.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deposit request: {str(e)}"
        )

# 36. POST /api/wallet/verify-deposit - Xác minh giao dịch nạp tiền
# @router.post("/verify-deposit", response_model=VerifyDepositResponse)
# async def verify_deposit(
#     verify_data: VerifyDepositRequest,
#     db: Session = Depends(get_db)
# ):
#     """Xác minh giao dịch nạp tiền dựa trên email từ ngân hàng (Admin / Cron)"""
#     try:
#         # Find pending transaction with this transfer code
#         transaction = db.query(WalletTransaction).filter(
#             WalletTransaction.note.like(f"%{verify_data.transfer_code}%"),
#             WalletTransaction.transaction_type == TransactionType.DEPOSIT,
#             WalletTransaction.status == TransactionStatus.PENDING
#         ).first()
        
#         if not transaction:
#             return VerifyDepositResponse(
#                 success=False,
#                 message="No pending transaction found with this transfer code",
#                 matched_tx=None
#             )
        
#         # Update transaction status to SUCCESS
#         transaction.status = TransactionStatus.SUCCESS
#         transaction.note = f"{transaction.note} - Verified and processed"
        
#         # Update wallet balance
#         wallet = db.query(Wallet).filter(Wallet.id == transaction.wallet_id).first()
#         if wallet:
#             wallet.balance += transaction.amount
#             wallet.total_deposited += transaction.amount
        
#         db.commit()
        
#         return VerifyDepositResponse(
#             success=True,
#             message="Deposit verified and processed successfully",
#             matched_tx={
#                 "id": str(transaction.id),
#                 "user_id": str(transaction.user_id),
#                 "amount": float(transaction.amount),
#                 "status": transaction.status
#             }
#         )
        
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to verify deposit: {str(e)}"
#         )

# 30. POST /api/orders/:id - Mua workflow bằng số dư ví
@router.post("/orders/{workflow_id}", response_model=PurchaseWithWalletResponse)
async def purchase_workflow_with_wallet(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mua workflow bằng số dư ví"""
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
        
        # Get or create wallet
        wallet = get_or_create_wallet(current_user.id, db)
        
        # Check if user has enough balance
        if wallet.balance < workflow.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance"
            )
        
        # Create purchase
        purchase = Purchase(
            id=uuid.uuid4(),
            user_id=current_user.id,
            workflow_id=workflow_id,
            amount=workflow.price,
            status="ACTIVE",
            payment_method="WALLET",
            paid_at=datetime.utcnow()
        )
        
        db.add(purchase)
        db.flush()  # Get the ID without committing
        
        # Create wallet transaction for purchase
        wallet_transaction = WalletTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            transaction_type=TransactionType.PURCHASE,
            amount=workflow.price,
            status=TransactionStatus.SUCCESS,
            reference_id=purchase.id,
            bank_name=None,
            bank_account=None,
            transfer_code=None,
            note=f"Purchase workflow: {workflow.title}"
        )
        
        db.add(wallet_transaction)
        
        # Update wallet balance
        wallet.balance -= workflow.price
        wallet.total_spent += workflow.price
        
        # Create invoice
        from app.models.invoice import Invoice
        invoice = Invoice(
            id=uuid.uuid4(),
            purchase_id=purchase.id,
            billing_name=current_user.name or "User",
            billing_email=current_user.email or "",
            amount=workflow.price
        )
        
        db.add(invoice)
        db.commit()
        
        return PurchaseWithWalletResponse(
            success=True,
            message="Workflow purchased successfully",
            wallet_balance=float(wallet.balance),
            purchase_id=purchase.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purchase workflow: {str(e)}"
        )

# Admin endpoint to activate deposit
@router.post("/admin/activate-deposit", response_model=AdminActivateDepositResponse)
async def admin_activate_deposit(
    request: AdminActivateDepositRequest,
    db: Session = Depends(get_db)
):
    """Admin endpoint to activate a pending deposit and add money to wallet"""
    try:
        # Find the pending deposit transaction
        transaction = db.query(WalletTransaction).filter(
            WalletTransaction.id == request.transaction_id,
            WalletTransaction.transaction_type == TransactionType.DEPOSIT,
            WalletTransaction.status == TransactionStatus.PENDING
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pending deposit transaction not found"
            )
        
        # Get the wallet
        wallet = db.query(Wallet).filter(Wallet.id == transaction.wallet_id).first()
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
        
        # Update transaction status to SUCCESS
        transaction.status = TransactionStatus.SUCCESS
        transaction.note = f"{transaction.note} - Activated by admin"
        
        # Update wallet balance
        wallet.balance += transaction.amount
        wallet.total_deposited += transaction.amount
        
        db.commit()
        db.refresh(wallet)
        db.refresh(transaction)
        
        # Send WebSocket notification to user with full transaction details
        await manager.send_personal_message({
            "type": "wallet_status_update",
            "event": "deposit_activated",
            "transaction": {
                "id": str(transaction.id),
                "status": transaction.status,
                "amount": float(transaction.amount),
                "bank_name": transaction.bank_name,
                "bank_account": transaction.bank_account,
                "transfer_code": transaction.transfer_code,
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None
            },
            "wallet": {
                "balance": float(wallet.balance),
                "total_deposited": float(wallet.total_deposited),
                "total_spent": float(wallet.total_spent)
            },
            "message": "Deposit transaction has been activated successfully",
            "timestamp": transaction.updated_at.isoformat() if transaction.updated_at else None
        }, str(wallet.user_id))
        
        return AdminActivateDepositResponse(
            success=True,
            message="Deposit activated successfully",
            transaction_id=transaction.id,
            user_id=wallet.user_id,
            amount=float(transaction.amount),
            new_wallet_balance=float(wallet.balance)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate deposit: {str(e)}"
        )
