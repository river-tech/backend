from sqlalchemy import Column, DateTime, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class WorkflowCategory(Base):
    __tablename__ = "workflow_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workflow = relationship("Workflow")
    category = relationship("Category")

    # Unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('workflow_id', 'category_id', name='uq_workflow_category'),
    )
