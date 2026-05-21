import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    # role = Column(String, default="user", nullable=False) # 'admin' or 'user'
    phone_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False)

    def __repr__(self):
        return f"<Role(user_id={self.user_id}, permission_id={self.permission_id})>"