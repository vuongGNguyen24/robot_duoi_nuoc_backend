from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
from app.api.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session
from app.schemas.telemetry import DashboardSummaryResponse, TelemetryRecordResponse
from app.models import Device, Sensor, Telemetry
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
            latest_sensor_telemetry.append({
                "sensor_id": sensor.id,
                "sensor_name": sensor.name,
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
    return []

@dashboard_router.get("/export", response_class=FileResponse)
async def export_report(
    start_date: datetime, 
    end_date: datetime, 
    format: str = "csv", 
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass
