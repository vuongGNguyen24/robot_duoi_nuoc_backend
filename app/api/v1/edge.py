from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.api.v1 import dependencies
from app.schemas.telemetry import EdgeTelemetryPayload, CameraImageResponse
from app.schemas.common import StandardErrorFormat
from app.schemas.actuator import ActuatorCommandResponse
from app.services.telemetry import telemetry_service
from app.services.storage import storage_service
from app.services.actuator import actuator_service
from app.api.v1.dependencies import verify_device_api_key

edge_router = APIRouter(prefix="/edge", tags=["Edge Devices"])

@edge_router.post("/telemetry", status_code=status.HTTP_202_ACCEPTED)
async def receive_telemetry(
    payload: EdgeTelemetryPayload, 
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_device_api_key),
    db: Session = Depends(dependencies.get_db)
):
    """
    Nhận dữ liệu quan trắc từ thiết bị biên (Edge device) qua HTTPS.
    Quá trình xử lý:
    1. Lưu dữ liệu vào bảng telemetry
    2. Kiểm tra ngưỡng các cảm biến môi trường (temperature, pH, DO...)
    3. Nếu vượt ngưỡng môi trường → gọi SMSService.send_alert() qua Background Task.
    """
    await telemetry_service.save_edge_telemetry(db, payload, background_tasks)
    return {"status": "accepted"}

@edge_router.post("/images", status_code=status.HTTP_202_ACCEPTED)
async def receive_camera_image(
    device_id: UUID = Form(...),
    captured_at: datetime = Form(...),
    image: UploadFile = File(...),
    api_key: str = Depends(verify_device_api_key),
    db: Session = Depends(dependencies.get_db)
):
    """
    Nhận ảnh chụp từ camera dưới nước, gửi kèm mỗi chu kỳ đo cảm biến.
    Quá trình xử lý:
    1. Validate file (định dạng JPEG/PNG, kích thước tối đa).
    2. Upload ảnh lên Object Storage (S3 / Viettel Object Storage).
    3. Lưu metadata (device_id, captured_at, image_url, file_size) vào DB bảng camera_images.
    4. Liên kết bản ghi ảnh với bản ghi telemetry gần nhất (theo device_id + thời gian).
    Lưu ý: API này nhận multipart/form-data, không phải JSON.
    """
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ hỗ trợ ảnh định dạng JPEG hoặc PNG"
        )
    
    # Đọc thử dữ liệu để kiểm tra size
    content = await image.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kích thước ảnh tối đa là 5MB"
        )
    await image.seek(0)
    
    res = await storage_service.save_camera_image(db, device_id, captured_at, image)
    return res

@edge_router.get("/commands/{device_id}", response_model=List[ActuatorCommandResponse])
async def poll_pending_commands(
    device_id: UUID,
    api_key: str = Depends(verify_device_api_key),
    db: Session = Depends(dependencies.get_db)
):
    """
    Edge device polling để lấy các lệnh điều khiển đang chờ thực thi.
    Trả về danh sách lệnh có status='queued' cho thiết bị tương ứng.
    Sau khi nhận lệnh, Edge device phải gọi PATCH /edge/commands/{command_id}/ack để xác nhận.
    """
    commands = actuator_service.get_queued_commands(db, device_id)
    
    return [
        ActuatorCommandResponse(
            command_id=cmd.id,
            device_id=cmd.device_id,
            command=cmd.command,
            status=cmd.status,
            created_at=cmd.created_at
        ) for cmd in commands
    ]

@edge_router.patch("/commands/{command_id}/ack", status_code=status.HTTP_200_OK)
async def acknowledge_command(
    command_id: UUID,
    api_key: str = Depends(verify_device_api_key),
    db: Session = Depends(dependencies.get_db)
):
    """
    Edge device xác nhận đã nhận và đang thực thi lệnh.
    Cập nhật trạng thái lệnh từ 'queued' → 'ack'.
    """
    command = actuator_service.acknowledge_command(db, command_id)
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lệnh yêu cầu"
        )
    
    return {"status": "success", "command_id": command_id, "state": "ack"}
