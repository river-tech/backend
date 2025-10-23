from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False)
    
    billing_name = Column(String(160), nullable=False)  # Buyer's name
    billing_email = Column(String(150), nullable=False)  # Email for billing
    
    amount = Column(Numeric(12, 2), nullable=False)  # Payment amount in VND
    issued_at = Column(DateTime(timezone=True), server_default=func.now())  # Invoice issue time
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    purchase = relationship("Purchase", back_populates="invoices")
