import uuid
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.database import Base
from geoalchemy2 import Geography


class MultiSensor(Base):
    __tablename__ = "multi_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    name = Column(String, nullable=False)
    locked_at = Column(DateTime, nullable=True)
    product_code = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    locked_at = Column(DateTime, nullable=True)


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    multi_sensor_id = Column(UUID(as_uuid=True), ForeignKey("multi_sensors.id"), nullable=False)
    sensor_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)

class DevicePosition(Base):
    __tablename__ = "device_positions"

    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), primary_key=True)
    time = Column(DateTime, primary_key=True, index=True, default=datetime.now())
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"), nullable=False)
    time = Column(DateTime, index=True, default=datetime.now(), nullable=False)
    unit = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    quality_flag = Column(Integer, nullable=True)
