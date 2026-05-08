from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class DeviceBase(BaseModel):
    name: str
    device_type: str
    firmware_version: Optional[str] = None
    location: Optional[str] = None

class DeviceCreate(DeviceBase):
    user_id: Optional[UUID4] = None

class DeviceResponse(DeviceBase):
    id: UUID4
    user_id: Optional[UUID4]
    installed_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class ThresholdUpdateRequest(BaseModel):
    sensor_id: UUID4 
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
