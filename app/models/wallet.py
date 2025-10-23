from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Numeric, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import TransactionType, TransactionStatus
import uuid


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    balance = Column(Numeric(14, 2), default=0.0, nullable=False)  # Số dư token hiện tại
    total_deposited = Column(Numeric(14, 2), default=0.0, nullable=False)  # Tổng đã nạp
    total_spent = Column(Numeric(14, 2), default=0.0, nullable=False)  # Tổng đã tiêu
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    
    transaction_type = Column(String(20), nullable=False)  # TransactionType enum
    amount = Column(Numeric(14, 2), nullable=False)  # Số tiền giao dịch
    status = Column(String(20), default="PENDING", nullable=False)  # TransactionStatus enum
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # có thể trỏ đến purchases.id
    
    # Thông tin nạp tiền
    bank_name = Column(String(100), nullable=True)  # Tên ngân hàng
    bank_account = Column(String(50), nullable=True)  # Số tài khoản
    transfer_code = Column(String(50), nullable=True)  # Mã giao dịch chuyển khoản
    
    note = Column(Text, nullable=True)  # Ghi chú giao dịch
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_wallet_transactions_wallet_created', 'wallet_id', 'created_at'),
    )
