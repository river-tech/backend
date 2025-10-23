from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import PurchaseStatus, PaymentMethod
import uuid


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    
    bank_account = Column(String(50), nullable=True)
    bank_name = Column(String(120), nullable=True)
    transfer_code = Column(String(60), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)  # Original price in VND
    status = Column(String(20), default="PENDING", nullable=False)  # PurchaseStatus enum
    payment_method = Column(String(10), default="QR", nullable=False)  # PaymentMethod enum
    paid_at = Column(DateTime(timezone=True), nullable=True)  # Payment timestamp
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    workflow = relationship("Workflow")
    invoices = relationship("Invoice", back_populates="purchase")
