from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)