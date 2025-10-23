from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import NotificationType
import uuid


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)  # NotificationType enum
    is_unread = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
