import uuid
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.database import Base
from geoalchemy2 import Geography

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    unit = Column(String, nullable=True)
    description = Column(String, nullable=True)

class DevicePosition(Base):
    __tablename__ = "device_positions"

    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), primary_key=True)
    time = Column(DateTime, primary_key=True, index=True)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)

class Telemetry(Base):
    __tablename__ = "telemetry"

    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"), primary_key=True)
    time = Column(DateTime, primary_key=True, index=True)
    value = Column(Float, nullable=True)
    quality_flag = Column(Integer, nullable=True)
    ingestion_time = Column(DateTime, default=datetime.utcnow)
