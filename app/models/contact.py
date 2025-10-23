from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String(160), nullable=False)
    email = Column(String(150), nullable=False)
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
