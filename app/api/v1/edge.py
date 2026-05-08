from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.api import dependencies
from app.schemas.telemetry import EdgeTelemetryPayload, CameraImageResponse
from app.schemas.common import StandardErrorFormat

from app.services.telemetry_service import telemetry_service

edge_router = APIRouter(prefix="/edge", tags=["Edge Devices"])

@edge_router.post("/telemetry", status_code=status.HTTP_202_ACCEPTED)
async def receive_telemetry(
    payload: EdgeTelemetryPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(dependencies.get_db),
    api_key: str = Depends(dependencies.verify_device_api_key)
):
    """
    Nhận dữ liệu quan trắc từ thiết bị biên (Edge device) qua HTTPS.
    Quá trình xử lý:
    1. Lưu dữ liệu vào bảng telemetry, device_positions.
    2. Kiểm tra ngưỡng các cảm biến môi trường (temperature, pH, DO...).
    3. Kiểm tra mức nước bồn chứa (water_level_raw): nếu dưới ngưỡng → ghi nhận cảnh báo bảo trì.
    4. Nếu vượt ngưỡng môi trường → gọi SMSService.send_alert() qua Background Task.
    5. Nếu mức nước thấp → gửi thông báo 'Cần bổ sung nước ngọt' lên Dashboard + SMS.
    """
    await telemetry_service.process_telemetry(db, payload, background_tasks)
    return {"message": "Telemetry data accepted for processing"}

from app.services.storage_service import storage_service

@edge_router.post("/images", response_model=CameraImageResponse, status_code=status.HTTP_202_ACCEPTED)
async def receive_image(
    device_id: UUID = Form(...),
    captured_at: datetime = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(dependencies.get_db),
    api_key: str = Depends(dependencies.verify_device_api_key)
):
    """
    Edge device gửi ảnh camera.
    Input: Form-data (multipart/form-data)
    """
    # Kiểm tra định dạng ảnh
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_IMAGE_FORMAT",
                "message": "File ảnh không đúng định dạng JPEG hoặc PNG."
            }
        )

    # Logic xử lý: Upload lên storage và lưu DB thông qua storage_service
    result = await storage_service.save_camera_image(db, device_id, captured_at, image)
    return result
