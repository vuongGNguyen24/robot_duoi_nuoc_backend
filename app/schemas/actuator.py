from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime

class ActuatorCommandRequest(BaseModel):
    device_id: UUID4
    command: str = Field(..., description="Lệnh điều khiển: 'lift_up' | 'lower_down' | 'start_cleaning' | 'stop_cleaning'")
    initiated_by: Optional[str] = Field(None, description="'manual' hoặc 'auto'")

class ActuatorCommandResponse(BaseModel):
    command_id: UUID4
    device_id: UUID4
    command: str
    status: str = Field(..., description="Trạng thái lệnh")
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class ActuatorStatusResponse(BaseModel):
    device_id: UUID4
    lift_status: str = Field(..., description="Trạng thái cơ cấu nâng hạ: 'up' | 'down' | 'moving'")
    cleaning_status: str = Field(..., description="Trạng thái cơ cấu xịt rửa: 'idle' | 'running'")
    last_cleaning_at: Optional[datetime] = Field(None, description="Thời điểm xịt rửa gần nhất")
    updated_at: datetime

class ActuatorCommandResponse(BaseModel):
    command_id: UUID4
    device_id: UUID4
    command: str
    status: str = Field(..., description="Trạng thái lệnh: 'queued' | 'sent' | 'ack' | 'failed'")
    created_at: datetime
