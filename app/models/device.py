import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    firmware_version = Column(String, nullable=True)
    location = Column(String, nullable=True)
    installed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
