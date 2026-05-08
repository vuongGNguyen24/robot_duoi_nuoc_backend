import uuid
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.core.database import Base

class CameraImage(Base):
    __tablename__ = "image_capture"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    captured_at = Column(DateTime, nullable=True)
    image_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

class ImageAnalysis(Base):
    __tablename__ = "image_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("image_capture.id"), nullable=True)
    result = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    processed_at = Column(DateTime, nullable=True)
