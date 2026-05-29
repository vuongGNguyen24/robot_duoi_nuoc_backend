# API Contract cho Hệ thống Robot Dưới Nước (FastAPI)

Tài liệu này định nghĩa API Contract dựa trên các Use Case và Database Schema. Cấu trúc được thiết kế nhắm tới việc dễ dàng chuyển đổi (hoặc tự động hóa) thành code FastAPI với Pydantic models.

## 1. Pydantic Models (Schemas)
Các model này dùng để validate dữ liệu đầu vào (Request) và định dạng dữ liệu đầu ra (Response).

```python
from pydantic import BaseModel, UUID4, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Base Models ---
class UserBase(BaseModel):
    username: str
    role: str = Field(..., description="Role of the user: 'admin' or 'user'")
    phone_number: Optional[str] = None

class DeviceBase(BaseModel):
    name: str
    device_type: str
    firmware_version: Optional[str] = None
    location: Optional[str] = None

# --- Request Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class SendOtpRequest(BaseModel):
    phone_number: str

class VerifyOtpRequest(BaseModel):
    phone_number: str
    otp: str

class ResetPasswordResponse(BaseModel):
    message: str
    new_password: str

class UpdatePhoneRequest(BaseModel):
    phone_number: str

class ThresholdUpdateRequest(BaseModel):
    sensor_id: UUID4 
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    otp: str = Field(..., description="Mã OTP xác thực để thực hiện thay đổi ngưỡng")

class EdgeTelemetryPayload(BaseModel):
    device_id: UUID4
    time: datetime
    location: Optional[str] = Field(None, description="Tọa độ GPS dạng WKT (Point)")
    sensors_data: List[Dict[str, Any]] = Field(..., description="Danh sách dữ liệu từ các sensor")
    quality_flag: Optional[int] = Field(None, description="Giá trị thô mức nước bồn chứa (%), gửi kèm mỗi lần đo telemetry")

class ActuatorCommandRequest(BaseModel):
    device_id: UUID4
    command: str = Field(..., description="Lệnh điều khiển: 'lift_up' | 'lower_down' | 'start_cleaning' | 'stop_cleaning'")
    initiated_by: Optional[str] = Field(None, description="'manual' (admin ra lệnh tay) hoặc 'auto' (hệ thống tự kích hoạt)")

# --- Response Models ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        orm_mode = True

class DeviceResponse(DeviceBase):
    id: UUID4
    user_id: Optional[UUID4]
    installed_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True

class DashboardSummaryResponse(BaseModel):
    total_devices: int
    active_alerts: int
    latest_telemetry: List[Dict[str, Any]]

class TelemetryRecordResponse(BaseModel):
    time: datetime
    device_id: UUID4
    device_name: Optional[str] = None
    location: Optional[Dict[str, float]] = Field(None, description="Tọa độ lat/lng, ví dụ: {'lat': 21.0, 'lng': 105.8}")
    readings: Dict[str, float] = Field(..., description="Các chỉ số linh hoạt: {'temperature': 26.5, 'pH': 7.2, 'dissolved_oxygen': 6.5, 'water_level_pct': 85.0}")
    alerts: List[str] = Field(default_factory=list, description="Các cảnh báo tại thời điểm đo (nếu có)")
    image_url: Optional[str] = Field(None, description="URL ảnh camera chụp tại thời điểm đo (nếu có). Ví dụ: 'https://storage.example.com/images/ROV_01_20240424T103000Z.jpg'")

class CameraImageResponse(BaseModel):
    id: UUID4
    device_id: UUID4
    captured_at: datetime
    image_url: str = Field(..., description="URL truy cập ảnh trên Object Storage (S3/Viettel)")
    file_size_bytes: Optional[int] = None
    linked_telemetry_time: Optional[datetime] = Field(None, description="Thời điểm đo telemetry tương ứng với ảnh này")

class WaterLevelStatusResponse(BaseModel):
    device_id: UUID4
    level_pct: float = Field(..., description="Mức nước bồn chứa hiện tại theo phần trăm (0–100%)")
    is_low: bool = Field(..., description="True nếu mức nước xuống dưới ngưỡng cảnh báo")
    low_threshold_pct: float = Field(..., description="Ngưỡng cảnh báo thấp đã cấu hình (mặc định 20%)")
    updated_at: datetime

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
```

---


## 2. API Endpoints (FastAPI Routers)

Dưới đây là chữ ký hàm (function signatures) tương ứng với các endpoints trong FastAPI.

### 2.1. Authentication Router (`/api/v1/auth`)
*Phục vụ Use case: Đăng nhập, Đổi mật khẩu, Lấy lại mật khẩu.*

```python
from fastapi import APIRouter, Depends, status

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """Xác thực người dùng và trả về JWT token."""
    pass

@auth_router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(payload: ChangePasswordRequest, current_user=Depends(get_current_user)):
    """Đổi mật khẩu cho người dùng đang đăng nhập."""
    pass

@auth_router.post("/send-otp", status_code=status.HTTP_202_ACCEPTED)
async def send_otp(payload: ForgotPasswordRequest):
    """Gửi SMS chứa OTP để lấy lại mật khẩu hoặc thực hiện tác vụ nhạy cảm."""
    pass

@auth_router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(payload: VerifyOtpRequest):
    """Xác thực mã OTP được gửi qua SMS."""
    pass

@auth_router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(payload: VerifyOtpRequest):
    """Đặt lại mật khẩu sau khi xác thực OTP thành công (trả về mật khẩu mới)."""
    pass
```

### 2.2. User Profile Router (`/api/v1/users`)
*Phục vụ Use case: Đổi số điện thoại.*

```python
users_router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@users_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user=Depends(get_current_user)):
    """Lấy thông tin tài khoản hiện tại."""
    pass

@users_router.put("/me/phone", response_model=UserResponse)
async def update_phone_number(payload: UpdatePhoneRequest, current_user=Depends(get_current_user)):
    """Cập nhật số điện thoại."""
    # Hệ thống sẽ tương tác với SMS System để xác thực số điện thoại nếu cần
    pass
```

### 2.3. Dashboard & Reports Router (`/api/v1/dashboard`)

*Phục vụ Use case: Xem thông tin dashboard, xuất báo cáo và cấp dữ liệu cho các biểu đồ (Charts).*

```python
from fastapi.responses import FileResponse

dashboard_router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

@dashboard_router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(current_user=Depends(get_current_user)):
    """
    Lấy thông tin tổng quan hiển thị trên Dashboard (số lượng thiết bị, số cảnh báo...).
    JSON Output mẫu:
    {
        "total_devices": 10,
        "active_alerts": 2,
        "latest_telemetry": [...]
    }
    """
    pass

@dashboard_router.get("/telemetry", response_model=List[TelemetryRecordResponse])
async def get_dashboard_telemetry(
    limit: int = 60,
    current_user=Depends(get_current_user)
):
    """
    Cấp dữ liệu time-series cho Frontend (Dashboard.tsx) để vẽ biểu đồ Nhiệt độ, pH, DO, Bản đồ (Heatmap) và AlertLog.
    Hỗ trợ cấu trúc linh hoạt (dynamic readings) cho các loại sensor khác nhau.
    Mỗi bản ghi có thể kèm image_url nếu camera chụp ảnh tại thời điểm đó.
    JSON Output mẫu (Mảng các object):
    [
        {
            "time": "2024-04-24T10:30:00Z",
            "device_id": "uuid...",
            "device_name": "ROV_01",
            "location": {"lat": 21.0285, "lng": 105.8542},
            "readings": {
                "temperature": 26.5,
                "pH": 7.4,
                "dissolved_oxygen": 6.8,
                "water_level_pct": 85.0
            },
            "alerts": ["Nhiệt độ cao bất thường"],
            "image_url": "https://storage.example.com/images/ROV_01_20240424T103000Z.jpg"
        }
    ]
    """
    pass

class ExportRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    columns: List[str]
    format: str = "csv" # "csv" or "xlsx"

# --- Response Models ---
# ... (rest of models)

# ... (in section 2.3)

@dashboard_router.post("/export")
async def export_report(
    payload: ExportRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xuất file báo cáo dữ liệu quan trắc.
    Lưu ý: API này nhận thông tin qua POST body và trả về stream byte của file (.csv, .xlsx) 
    với header 'Content-Disposition: attachment; filename=report.csv'.
    """
    pass

```

### 2.4. Admin Management Router (`/api/v1/admin`)
*Phục vụ Use case: Quản lý thiết bị, Quản lý tài khoản, Sửa ngưỡng cảnh báo.*

```python
admin_router = APIRouter(prefix="/api/v1/admin", tags=["Admin"], dependencies=[Depends(require_admin_role)])

# --- User Management ---
@admin_router.get("/users", response_model=List[UserResponse])
async def list_users():
    """Lấy danh sách tài khoản (trừ tài khoản admin)."""
    pass

@admin_router.get("/users/role/{role}", response_model=List[UserResponse])
async def list_users_by_role(role: Literal["moderator", "user"]):
    """Lấy danh sách các tài khoản theo role (moderator hoặc user)."""
    pass

@admin_router.get("/users/details/{user_id}", response_model=UserResponse)
async def get_user_details(user_id: UUID4):
    """Xem chi tiết một tài khoản (Admin only)."""
    pass


@admin_router.put("/users/details/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_details(user_id: UUID4, payload: UserUpdate):
    """Cập nhật thông tin chi tiết một tài khoản (Admin only)."""
    pass

@admin_router.put("/users/lock/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_lock(user_id: UUID4, payload: UserUpdate):
    """Khóa (Delete) một tài khoản (Admin only)."""
    pass


@admin_router.post("/users", response_model=UserResponse)
async def create_user(payload: UserBase):
    """Tạo tài khoản mới."""
    pass

# --- Device Management ---
@admin_router.get("/devices", response_model=List[DeviceResponse])
async def list_devices():
    """Lấy danh sách thiết bị."""
    pass

@admin_router.post("/devices", response_model=DeviceResponse)
async def create_device(payload: DeviceBase):
    """Tạo thiết bị mới."""
    pass

@admin_router.get("/devices/{device_id}", response_model=DeviceDetailResponse)
async def get_device(device_id: UUID4):
    """Lấy chi tiết một thiết bị kèm danh sách cảm biến."""
    pass

# --- Device Allocation ---
@admin_router.post("/users/devices", status_code=status.HTTP_201_CREATED)
async def assign_device_to_user(payload: UserDeviceAssignment):
    """Phân bổ thiết bị cho user (ghi vào bảng device_management_logs)."""
    pass

@admin_router.delete("/users/devices", status_code=status.HTTP_200_OK)
async def remove_device_from_user(payload: UserDeviceRemoval):
    """Gỡ bỏ thiết bị khỏi user (cập nhật bảng device_management_logs)."""
    pass

@admin_router.post("/moderators/devices", status_code=status.HTTP_201_CREATED)
async def assign_device_to_moderator(payload: ModDeviceAssignment):
    """Phân bổ thiết bị cho moderator (ghi vào bảng mods_devices)."""
    pass

@admin_router.delete("/moderators/devices", status_code=status.HTTP_200_OK)
async def remove_device_from_moderator(payload: ModDeviceRemoval):
    """Gỡ bỏ thiết bị khỏi moderator (cập nhật bảng mods_devices)."""
    pass
```

### 2.5. Edge Device Router (`/api/v1/edge`)
*Phục vụ Use case: Gửi dữ liệu quan trắc và ảnh camera (từ Edge device).*

```python
edge_router = APIRouter(prefix="/api/v1/edge", tags=["Edge Device"])

@edge_router.post("/telemetry", status_code=status.HTTP_202_ACCEPTED)
async def receive_telemetry(
    payload: EdgeTelemetryPayload, 
    api_key: str = Depends(verify_device_api_key)
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
    pass

@edge_router.post("/images", status_code=status.HTTP_202_ACCEPTED)
async def receive_camera_image(
    device_id: UUID4,
    captured_at: datetime,
    image: UploadFile = File(...),
    api_key: str = Depends(verify_device_api_key)
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
    pass

@edge_router.get("/commands/{device_id}", response_model=List[ActuatorCommandResponse])
async def poll_pending_commands(
    device_id: UUID4,
    api_key: str = Depends(verify_device_api_key)
):
    """
    Edge device polling để lấy các lệnh điều khiển đang chờ thực thi.
    Trả về danh sách lệnh có status='queued' cho thiết bị tương ứng.
    Sau khi nhận lệnh, Edge device phải gọi PATCH /edge/commands/{command_id}/ack để xác nhận.
    """
    pass

@edge_router.patch("/commands/{command_id}/ack", status_code=status.HTTP_200_OK)
async def acknowledge_command(
    command_id: UUID4,
    api_key: str = Depends(verify_device_api_key)
):
    """
    Edge device xác nhận đã nhận và đang thực thi lệnh.
    Cập nhật trạng thái lệnh từ 'queued' → 'ack'.
    """
    pass
```

### 2.6. Actuator Control Router (`/api/v1/actuators`)
*Phục vụ Use case: Admin điều khiển cơ cấu nâng hạ và xịt rửa cảm biến + camera.*

```python
actuator_router = APIRouter(prefix="/api/v1/actuators", tags=["Actuators"], dependencies=[Depends(require_admin_role)])

@actuator_router.post("/commands", response_model=ActuatorCommandResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_actuator_command(payload: ActuatorCommandRequest):
    """
    Admin gửi lệnh điều khiển thiết bị chấp hành xuống Edge device.
    Các lệnh hợp lệ:
      - 'lift_up'        : Kéo cụm cảm biến + camera lên mặt nước (chuẩn bị xịt rửa).
      - 'lower_down'     : Thả cụm cảm biến + camera xuống độ sâu tiêu chuẩn (tiếp tục quan trắc).
      - 'start_cleaning' : Kích hoạt máy bơm và cơ cấu vòi phun xịt rửa.
      - 'stop_cleaning'  : Dừng máy bơm và cơ cấu vòi phun.
    Lệnh được lưu vào DB với status='queued'. Edge device sẽ lấy lệnh qua GET /edge/commands/{device_id}.
    Lưu ý: Nên thực hiện theo thứ tự: lift_up → start_cleaning → stop_cleaning → lower_down.
    """
    pass

@actuator_router.get("/status/{device_id}", response_model=ActuatorStatusResponse)
async def get_actuator_status(device_id: UUID4):
    """
    Lấy trạng thái hiện tại của cơ cấu nâng hạ và xịt rửa cho một thiết bị.
    Trạng thái được cập nhật khi Edge device gửi telemetry hoặc ack lệnh.
    """
    pass


---

## 3. Hệ thống External (SMS & AI)
Trong mã nguồn FastAPI, các hệ thống bên ngoài sẽ được tổ chức dưới dạng các `Services` tích hợp trực tiếp trên Server.

*   **Quy tắc gửi SMS**:
    1.  **Server-side Trigger**: Chỉ Server mới có quyền gọi đến SMS Provider API.
    2.  **Logic**:
        -   Khi nhận `/telemetry` từ Edge device, Server thực hiện so khớp ngưỡng (Threshold check).
        -   Nếu vi phạm ngưỡng môi trường, Server khởi tạo Background Task để gửi SMS cảnh báo.
        -   Nếu `water_level_pct` dưới ngưỡng, Server gửi SMS bảo trì: "Cần bổ sung nước ngọt tại trạm [tên trạm]".
        -   Đối với `reset-password` và các tác vụ nhạy cảm (như thay đổi ngưỡng `settings/thresholds`), Server sinh mã OTP, lưu vào Redis/DB với thời hạn ngắn và gửi qua SMS.

*   **Quy tắc lưu trữ ảnh Camera**:
    1.  Ảnh từ Edge device gửi lên qua `POST /edge/images` (multipart/form-data).
    2.  Server upload ảnh lên Object Storage (AWS S3 hoặc Viettel Object Storage), lưu metadata vào DB.
    3.  `image_url` được gắn vào bản ghi telemetry tương ứng để Frontend hiển thị kèm dữ liệu đo.

*   **Service Methods (Backend)**:
    -   `SMSService.send_alert(phone_number, message)`: Gửi tin nhắn cảnh báo khi có sự cố dữ liệu.
    -   `SMSService.send_otp(phone_number, otp)`: Gửi mã OTP để xác thực tài khoản hoặc khôi phục mật khẩu.
    -   `SMSService.send_maintenance(phone_number, message)`: Gửi cảnh báo bảo trì (ví dụ: mức nước bồn thấp).
    -   `StorageService.upload_image(file, device_id, captured_at) -> str`: Upload ảnh lên Object Storage và trả về URL công khai.
    -   `ActuatorService.enqueue_command(device_id, command, initiated_by)`: Ghi lệnh điều khiển vào DB để Edge device polling.
