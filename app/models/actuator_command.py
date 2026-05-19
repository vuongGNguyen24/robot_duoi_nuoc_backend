import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.database import Base

class ActuatorCommand(Base):
    __tablename__ = "actuator_commands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    command = Column(String, nullable=False)
    initiated_by = Column(String, nullable=True)
    status = Column(String, default="queued") # 'queued', 'sent', 'ack', 'failed'
    created_at = Column(DateTime, default=datetime.now())
