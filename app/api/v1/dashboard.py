from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.v1.dependencies import get_current_user, get_db, validate_user_device_ownership
from app.schemas.telemetry import DashboardSummaryResponse, TelemetryRecordResponse, ExportRequest
from app.schemas.device import DeviceResponse
from app.services.telemetry import telemetry_service

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@dashboard_router.get("/devices", response_model=List[DeviceResponse])
async def get_dashboard_devices(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    devices = telemetry_service.get_dashboard_devices(db, current_user.id)
    if not devices:
        raise HTTPException(status_code=404, detail="No devices found for this user")
    return [DeviceResponse.from_orm(device) for device in devices]


@dashboard_router.get("/summary/device_id={device_id}")
async def get_dashboard_summary_by_device(device_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    #validate user own this device
    device = telemetry_service.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    validate_user_device_ownership(device_id, current_user, db)
    
    return telemetry_service.get_device_summary(db, device_id)


@dashboard_router.get("/telemetry/device_id={device_id}", response_model=List[TelemetryRecordResponse])
async def get_dashboard_telemetry_by_device(
    device_id: UUID,
    limit: int = 60,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #validate user own this device
    device = telemetry_service.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    validate_user_device_ownership(current_user.id, device_id, db)
    
    return telemetry_service.get_dashboard_telemetry(db, device, limit)


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
    device = telemetry_service.get_device_by_id(db, payload.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    validate_user_device_ownership(current_user.id, payload.device_id, db)
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
