from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.v1.dependencies import get_current_user, get_db, validate_user_ownership
from app.schemas.telemetry import DashboardSummaryResponse, TelemetryRecordResponse, ExportRequest
from app.schemas.device import DeviceResponse
from app.models import Device, Sensor, Telemetry, DevicePosition, CameraImage, DeviceManagementLog
from app.services.telemetry_service import telemetry_service

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@dashboard_router.get("/devices", response_model=List[DeviceResponse])
async def get_dashboard_devices(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.id
    device_ids = db.query(DeviceManagementLog.device_id).filter(DeviceManagementLog.user_id == user_id).filter(DeviceManagementLog.removed_at == None).all()
    if not device_ids:
        raise HTTPException(status_code=404, detail="No devices found for this user")
    devices = db.query(Device).filter(Device.id.in_([device_id[0] for device_id in device_ids])).filter(Device.is_locked == True).all()
    return [DeviceResponse.from_orm(device) for device in devices]


@dashboard_router.get("/summary/device_id={device_id}")
async def get_dashboard_summary_by_device(device_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    #validate user own this device
    device = db.query(Device).filter(Device.id == device_id).filter(Device.is_locked == True).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    validate_user_ownership(current_user.id, device_id, db)
    
    sensors = db.query(Sensor).filter(Sensor.device_id == device.id).all()
    latest_sensor_telemetry = []
    # query the latest telemetry for each sensor
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
        "active_alerts": 0,
        "latest_telemetry": latest_sensor_telemetry
    }


@dashboard_router.get("/telemetry/device_id={device_id}", response_model=List[TelemetryRecordResponse])
async def get_dashboard_telemetry_by_device(
    device_id: UUID,
    limit: int = 60,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #validate user own this device
    device = db.query(Device).filter(Device.id == device_id).filter(Device.is_locked == True).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    validate_user_ownership(current_user.id, device_id, db)
    
    device_ids = [device_id]
    device_map = {device_id: device.name}

    # 2. Truy vấn dữ liệu Telemetry kèm thông tin Sensor
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



@dashboard_router.post("/export")
async def export_report(
    payload: ExportRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xuất báo cáo định dạng CSV hoặc XLSX dựa trên payload.
    Lưu ý: API này nhận thông tin xuất qua body (POST) để hỗ trợ danh sách cột linh hoạt.
    """
    device = db.query(Device).filter(Device.id == payload.device_id).filter(Device.is_locked == True).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    validate_user_ownership(current_user.id, payload.device_id, db)
    output, filename, media_type = await telemetry_service.export_telemetry_data(
        db=db,
        device_id=payload.device_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        columns=payload.columns,
        format=payload.format
    )
    
    if not output:
        return {"message": "No data found to export"}

    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(output, media_type=media_type, headers=headers)
