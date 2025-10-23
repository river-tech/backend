from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, Numeric, Integer, BigInteger, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.enums import WorkflowStatus
import uuid


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default="active", nullable=False)  # WorkflowStatus enum
    features = Column(ARRAY(Text), nullable=True)  # Array of features
    downloads_count = Column(BigInteger, default=0, nullable=False)
    time_to_setup = Column(Integer, nullable=True)
    video_demo = Column(String, nullable=True)
    flow = Column(JSON, nullable=True)  # JSONB workflow definition
    rating_avg = Column(Numeric(3, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    # Links to pivot table WorkflowCategory; used as Workflow.categories in queries
    categories = relationship("WorkflowCategory", cascade="all, delete-orphan")
    # Workflow assets (images, docs, etc.)
    assets = relationship("WorkflowAsset", cascade="all, delete-orphan")
    # Users' favorites for this workflow
    favorites = relationship("Favorite", cascade="all, delete-orphan")
    # Comments / reviews
    comments = relationship("Comment", cascade="all, delete-orphan")
