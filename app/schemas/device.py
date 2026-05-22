from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime
from app.schemas.sensor import SensorResponse

class DeviceBase(BaseModel):
    name: str
    device_type: str
    firmware_version: Optional[str] = None
    location: Optional[str] = None

class DeviceCreate(DeviceBase):
    installed_at: Optional[datetime]

class DeviceResponse(DeviceBase):
    id: UUID4
    installed_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class DeviceDetailResponse(DeviceResponse):
    sensors: List[SensorResponse] = []

class ThresholdUpdateRequest(BaseModel):
    sensor_id: UUID4 
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None

class UserDeviceAssignment(BaseModel):
    user_id: UUID4
    device_id: UUID4
    notes: Optional[str] = None

class UserDeviceRemoval(BaseModel):
    user_id: UUID4
    device_id: UUID4
    notes: Optional[str] = None

class ModDeviceAssignment(BaseModel):
    mod_id: UUID4
    device_id: UUID4
    notes: Optional[str] = None

class ModDeviceRemoval(BaseModel):
    mod_id: UUID4
    device_id: UUID4
    notes: Optional[str] = None

