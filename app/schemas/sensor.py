from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime



class SensorBase(BaseModel):
    name: str
    description: Optional[str]
    sensor_type: Optional[str]

class SensorCreate(SensorBase):
    multi_sensor_id: UUID4


class SensorResponse(SensorBase):
    id: UUID4
    multi_sensor_id: UUID4

    class Config:
        orm_mode = True
        from_attributes = True


class MultiSensorBase(BaseModel):
    name: str
    product_code: str
    vendor: str
    description: Optional[str]
    
class MultiSensorCreate(MultiSensorBase):
    device_id: UUID4

class MultiSensorResponse(MultiSensorBase):
    id: UUID4
    device_id: UUID4

    class Config:
        orm_mode = True
        from_attributes = True
        
class MultiSensorDetailResponse(MultiSensorResponse):
    sensors: List[SensorResponse]