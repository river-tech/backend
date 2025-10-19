from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(120), nullable=True)
    avatar_url = Column(String, nullable=True)
    email = Column(String(150), unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(String, default='USER', nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
