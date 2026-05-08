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
    lift_status: str = Field(..., description="Trạng thái cơ cấu nâng hạ")
    cleaning_status: str = Field(..., description="Trạng thái cơ cấu xịt rửa")
    last_cleaning_at: Optional[datetime] = Field(None, description="Thời điểm xịt rửa gần nhất")
    updated_at: datetime

class WaterLevelStatusResponse(BaseModel):
    device_id: UUID4
    level_pct: float = Field(..., description="Mức nước bồn chứa hiện tại (%)")
    is_low: bool = Field(..., description="True nếu mức nước xuống dưới ngưỡng")
    low_threshold_pct: float = Field(..., description="Ngưỡng cảnh báo thấp")
    updated_at: datetime
