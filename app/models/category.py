from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
