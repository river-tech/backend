from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class WorkflowAsset(Base):
    __tablename__ = "workflow_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    asset_url = Column(Text, nullable=False)
    kind = Column(String(30), default="image", nullable=False)  # image, video, zip, doc...
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workflow = relationship("Workflow")
