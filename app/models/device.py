import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.database import Base





class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=True)
    firmware_version = Column(String, nullable=True)
    location = Column(String, nullable=True)
    installed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    device_api_key_hash = Column(String, unique=True, nullable=False)
    salt = Column(String, nullable=False)
    def __repr__(self):
        return f"<Device(id='{self.id}', name='{self.name}')>"

class DeviceManagementLog(Base):
    __tablename__ = "device_management_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    create_at = Column(DateTime, default=datetime.now, nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    removed_at = Column(DateTime, nullable=True)
    removed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

class ModsDevice(Base):
    __tablename__ = "mods_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mod_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    granted_at = Column(DateTime, default=datetime.now, nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
