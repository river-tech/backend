from sqlalchemy import Column, DateTime, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    workflow = relationship("Workflow")

    # Unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('user_id', 'workflow_id', name='uq_user_workflow_favorite'),
    )
