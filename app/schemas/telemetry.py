from pydantic import BaseModel, UUID4, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EdgeTelemetryPayload(BaseModel):
    """
    Ví dụ:
    {
        "sensor_name": "Cảm biến nhiệt độ nước",
        "sensor_value": 26.5,
        "unit": "°C",
        "quality_flag": 1
    }
    """
    sensor_name: str
    time: datetime
    sensor_value: float = Field(..., description="Dữ liệu từ các sensor")
    unit: str = Field(..., description="Đơn vị của dữ liệu")
    quality_flag: Optional[int] = Field(..., description="Chất lượng đo từ các sensor")



class EdgePositionPayload(BaseModel):
    """
    Ví dụ:
    {
        "device_name": "ROV_01",
        "location": "POINT(105.8542 21.0285)"
    }
    """
    device_id: UUID4
    location: str = Field(..., description="Tọa độ GPS dạng WKT (Point)")
class TelemetryRecordResponse(BaseModel):
    time: datetime
    device_id: UUID4
    device_name: Optional[str] = None
    location: Optional[Dict[str, float]] = Field(None, description="Tọa độ lat/lng")
    readings: Dict[str, float] = Field(..., description="Các chỉ số linh hoạt")
    alerts: List[str] = Field(default_factory=list, description="Các cảnh báo")
    image_url: Optional[str] = Field(None, description="URL ảnh camera")

class DashboardSummaryResponse(BaseModel):
    total_devices: int
    active_alerts: int
    latest_telemetry: List[Dict[str, Any]]

class CameraImageResponse(BaseModel):
    id: UUID4
    device_id: UUID4
    captured_at: datetime
    image_url: str = Field(..., description="URL truy cập ảnh")
    file_size_bytes: Optional[int] = None
    linked_telemetry_time: Optional[datetime] = Field(None, description="Thời điểm đo telemetry")

class ExportRequest(BaseModel):
    device_id: UUID4
    start_date: datetime
    end_date: datetime
    columns: List[str]
    format: str = "csv"  # "csv" or "xlsx"

