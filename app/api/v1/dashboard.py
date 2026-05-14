from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
from app.api.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session
from app.schemas.telemetry import DashboardSummaryResponse, TelemetryRecordResponse
from app.models import Device, Sensor, Telemetry, DevicePosition, CameraImage

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@dashboard_router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    #user and device is 1 - 1 relationship, so we can directly query devices by user_id
    devices = db.query(Device).filter(Device.user_id == current_user.id)
    #get last telemetry for each device
    latest_sensor_telemetry = []
    for device in devices:
        #query all sensors for this device
        sensors = db.query(Sensor).filter(Sensor.device_id == device.id).all()
        #query the latest telemetry for each sensor
        for sensor in sensors:
            telemetry = db.query(Telemetry).filter(Telemetry.sensor_id == sensor.id).order_by(Telemetry.time.desc()).first()
            if telemetry:
                latest_sensor_telemetry.append({
                    "sensor_id": sensor.id,
                    "sensor_name": sensor.description or f"Sensor {sensor.id}",
                    "value": telemetry.value,
                    "time": telemetry.time
                })
    return {
        "total_devices": devices.count(),
        "active_alerts": 0,
        "latest_telemetry": latest_sensor_telemetry
    }

@dashboard_router.get("/telemetry", response_model=List[TelemetryRecordResponse])
async def get_dashboard_telemetry(
    limit: int = 60,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Lấy danh sách thiết bị của người dùng hiện tại
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()
    if not devices:
        return []
    
    device_ids = [d.id for d in devices]
    device_map = {d.id: d.name for d in devices}

    # 2. Truy vấn dữ liệu Telemetry kèm thông tin Sensor
    # Chúng ta lấy nhiều hơn limit một chút để sau khi group theo (time, device) vẫn đủ data
    raw_telemetry = (
        db.query(Telemetry, Sensor.device_id, Sensor.description)
        .join(Sensor, Telemetry.sensor_id == Sensor.id)
        .filter(Sensor.device_id.in_(device_ids))
        .order_by(Telemetry.time.desc())
        .limit(limit * 5)
        .all()
    )

    # 3. Gom nhóm dữ liệu theo (device_id, time) để tạo object TelemetryRecordResponse
    records_dict = {}
    for t, device_id, sensor_desc in raw_telemetry:
        key = (device_id, t.time)
        if key not in records_dict:
            if len(records_dict) >= limit:
                break
            records_dict[key] = {
                "time": t.time,
                "device_id": device_id,
                "device_name": device_map.get(device_id),
                "readings": {},
                "alerts": [],
                "location": None,
                "image_url": None
            }
        
        # Format key cho readings (ví dụ: "Nhiệt độ" -> "nhiet_do")
        reading_key = sensor_desc.lower().replace(" ", "_") if sensor_desc else "value"
        records_dict[key]["readings"][reading_key] = t.value

    # 4. Bổ sung thông tin Location và Image cho từng bản ghi
    final_records = list(records_dict.values())
    for record in final_records:
        # Lấy vị trí gần nhất với thời điểm record
        pos = db.query(DevicePosition).filter(
            DevicePosition.device_id == record["device_id"],
            DevicePosition.time <= record["time"]
        ).order_by(DevicePosition.time.desc()).first()
        
        if pos:
            # Lưu ý: Trong SQLite PoC, location được mock là string hoặc POINT
            # Ở đây giả lập trả về tọa độ cố định hoặc parse từ string nếu cần
            record["location"] = {"lat": 21.0285, "lng": 105.8542}

        # Lấy ảnh gần nhất
        img = db.query(CameraImage).filter(
            CameraImage.device_id == record["device_id"],
            CameraImage.captured_at <= record["time"]
        ).order_by(CameraImage.captured_at.desc()).first()
        
        if img:
            record["image_url"] = img.image_url

    return final_records

@dashboard_router.get("/export", response_class=FileResponse)
async def export_report(
    start_date: datetime, 
    end_date: datetime, 
    format: str = "csv", 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass
