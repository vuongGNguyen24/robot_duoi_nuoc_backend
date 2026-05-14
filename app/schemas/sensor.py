from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

# CREATE TABLE "sensors" (
#   "id" uuid PRIMARY KEY,
#   "device_id" uuid NOT NULL,
#   "unit" varchar,
#   "description" varchar
# );
class SensorBase(BaseModel):
    unit: str
    description: Optional[str]
    

class SensorCreate(SensorBase):
    device_id: UUID4


class SensorResponse(SensorBase):
    id: UUID4
    device_id: UUID4

    class Config:
        orm_mode = True
        from_attributes = True