from pydantic import BaseModel, UUID4, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EdgeTelemetryPayload(BaseModel):
    device_id: UUID4
    time: datetime
    location: Optional[str] = Field(None, description="Tọa độ GPS dạng WKT (Point)")
    sensors_data: List[Dict[str, Any]] = Field(..., description="Danh sách dữ liệu từ các sensor")
    water_level_raw: Optional[float] = Field(None, description="Giá trị thô mức nước bồn chứa (%)")

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

