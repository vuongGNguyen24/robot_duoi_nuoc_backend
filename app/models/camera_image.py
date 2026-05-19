import uuid
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
from app.core.database import Base

class CameraImage(Base):
    __tablename__ = "image_capture"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    captured_at = Column(DateTime, default=datetime.now(), nullable=False)
    image_url = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

class ImageAnalysis(Base):
    __tablename__ = "image_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("image_capture.id"), nullable=False)
    result = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=True)
    processed_at = Column(DateTime, default=datetime.now(), nullable=False)
