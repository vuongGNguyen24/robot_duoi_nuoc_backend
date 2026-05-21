# API Contract - Examples & Error Codes

Tài liệu này bổ sung cho API Contract chính, cung cấp các ví dụ cụ thể về dữ liệu Input/Output cho các phương thức `GET` và định nghĩa quy chuẩn mã lỗi cho toàn hệ thống.

---

## 1. Dữ liệu Input / Output cho các phương thức `GET`

Trong thiết kế RESTful API chuẩn, các phương thức `GET` **không sử dụng JSON body** để làm đầu vào. Thay vào đó, dữ liệu đầu vào (Input) sẽ được truyền qua **Query Parameters** (trên URL) hoặc **Path Parameters**. Đầu ra (Output) sẽ luôn là định dạng JSON.

### 1.1. Lấy thông tin tài khoản hiện tại (`GET /api/v1/users/me`)

- **Input (Headers):** Yêu cầu truyền `Authorization: Bearer <token>`
- **Input (Parameters):** Không có
- **Output JSON (Thành công - 200 OK):**

```json
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin_robot",
    "role": "admin",
    "phone_number": "0123456789",
    "created_at": "2024-04-24T10:00:00Z"
 
 }
```

### 1.2. Lấy thông tin Dashboard Summary (`GET /api/v1/dashboard/summary`)

- **Input (Query Parameters):** Có thể nhận các tham số để lọc (Tùy chọn)
- Ví dụ URL: `/api/v1/dashboard/summary?time_range=24h&device_id=abc...`
- **Output JSON (Thành công - 200 OK):**

```json
  {
    "total_devices": 15,
    "active_alerts": 2,
    "latest_telemetry": [
      {
        "time": "2024-04-24T10:30:00Z",
        "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
        "device_name": "ROV_01",
        "location": { "lat": 21.0285, "lng": 105.8542 },
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
  }
```

### 1.3. Lấy dữ liệu biểu đồ Telemetry (`GET /api/v1/dashboard/telemetry`)

- **Input (Query Parameters):** Dùng để lọc số lượng hoặc khoảng thời gian.
  - Ví dụ URL: `/api/v1/dashboard/telemetry?limit=60`
- **Output JSON (Thành công - 200 OK) (Mảng Array):**
  
  ```json
  [
    {
      "time": "2024-04-24T10:30:00Z",
      "device_id": "a1b2c3d4...",
      "device_name": "ROV_01",
      "location": { "lat": 21.0285, "lng": 105.8542 },
      "readings": {
        "temperature": 26.5,
        "pH": 7.4,
        "dissolved_oxygen": 6.8,
        "water_level_pct": 85.0
      },
      "alerts": ["Nhiệt độ cao bất thường"],
      "image_url": "https://storage.example.com/images/ROV_01_20240424T103000Z.jpg"
    },
    {
      "time": "2024-04-24T10:32:00Z",
      "device_id": "a1b2c3d4...",
      "device_name": "ROV_01",
      "location": { "lat": 21.0285, "lng": 105.8542 },
      "readings": {
        "temperature": 26.6,
        "pH": 7.3,
        "dissolved_oxygen": 6.7,
        "water_level_pct": 84.5
      },
      "alerts": [],
      "image_url": null
    }
  ]
  ```

  > **Ghi chú:** `image_url` là `null` nếu camera không gửi ảnh trong chu kỳ đó (ví dụ: lỗi truyền hoặc chưa có ảnh mới).

### 1.4. Lấy danh sách người dùng - Admin (`GET /api/v1/admin/users`)

- **Input (Query Parameters):** Dùng để phân trang và tìm kiếm.
  - Ví dụ URL: `/api/v1/admin/users?page=1&limit=10&search=admin_robot`
- **Output JSON (Thành công - 200 OK) (Trả về một Mảng Array):**

  ```json
  [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "admin_robot",
      "role": "admin",
      "phone_number": "0987654321",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "987fcdeb-51a2-43d7-90ab-cdef12345678",
      "username": "user_underwater_01",
      "role": "user",
      "phone_number": null,
      "created_at": "2024-02-15T09:30:00Z"
    }
  ]
  ```

### 1.5. Lấy danh sách thiết bị - Admin (`GET /api/v1/admin/devices`)

- **Input (Query Parameters):**
  - Ví dụ URL: `/api/v1/admin/devices?status=active&type=underwater_drone`
- **Output JSON (Thành công - 200 OK) (Trả về một Mảng Array):**
  ```json
  [
    {
      "id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
      "name": "ROV_01",
      "device_type": "Underwater Drone",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "firmware_version": "v1.2.0",
      "location": "Hồ Tây",
      "installed_at": "2024-03-15T08:00:00Z",
      "created_at": "2024-03-10T10:00:00Z"
    }
  ]
  ```

### 1.6. Lấy trạng thái thiết bị chấp hành (`GET /api/v1/actuators/status/{device_id}`)

- **Input (Path Parameter):** `device_id` (UUID của thiết bị)
- **Input (Headers):** Yêu cầu Admin token
- **Output JSON (Thành công - 200 OK):**
  ```json
  {
    "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
    "lift_status": "down",
    "cleaning_status": "idle",
    "last_cleaning_at": "2024-04-24T08:00:00Z",
    "updated_at": "2024-04-24T10:30:00Z"
  }
  ```
  > **Các giá trị hợp lệ:**
  >
  > - `lift_status`: `"up"` (đã kéo lên) | `"down"` (đang trong nước) | `"moving"` (đang di chuyển)
  > - `cleaning_status`: `"idle"` (không hoạt động) | `"running"` (đang xịt rửa)

### 1.7. Lấy trạng thái mức nước bồn chứa (`GET /api/v1/actuators/water-level/{device_id}`)

- **Input (Path Parameter):** `device_id` (UUID của thiết bị)
- **Input (Headers):** Yêu cầu Admin token
- **Output JSON (Thành công - 200 OK):**
  ```json
  {
    "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
    "level_pct": 18.5,
    "is_low": true,
    "low_threshold_pct": 20.0,
    "updated_at": "2024-04-24T10:30:00Z"
  }
  ```
  > **Ghi chú:** Khi `is_low = true`, hệ thống đã tự động gửi cảnh báo bảo trì qua Dashboard và SMS tới số điện thoại quản lý.

### 1.8. Lấy danh sách ảnh camera (`GET /api/v1/dashboard/images`)

- **Input (Query Parameters):** Dùng để lọc theo thiết bị và thời gian.
  - Ví dụ URL: `/api/v1/dashboard/images?device_id=a1b2c3d4...&limit=20`
- **Output JSON (Thành công - 200 OK) (Mảng Array):**
  ```json
  [
    {
      "id": "f1e2d3c4-5678-90ab-cdef-123456789abc",
      "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
      "captured_at": "2024-04-24T10:30:00Z",
      "image_url": "https://storage.example.com/images/ROV_01_20240424T103000Z.jpg",
      "file_size_bytes": 245760,
      "linked_telemetry_time": "2024-04-24T10:30:00Z"
    },
    {
      "id": "a9b8c7d6-5432-10fe-dcba-987654321fed",
      "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
      "captured_at": "2024-04-24T10:25:00Z",
      "image_url": "https://storage.example.com/images/ROV_01_20240424T102500Z.jpg",
      "file_size_bytes": 231400,
      "linked_telemetry_time": "2024-04-24T10:25:00Z"
    }
  ]
  ```

---

## 2. Dữ liệu Input / Output cho các phương thức `POST` / `PATCH` (mới bổ sung)

### 2.1. Gửi lệnh điều khiển thiết bị chấp hành (`POST /api/v1/actuators/commands`)

- **Input (Headers):** Yêu cầu Admin token
- **Input (JSON Body):**

  ```json
  {
    "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
    "command": "lift_up",
    "initiated_by": "manual"
  }
  ```

  > **Các lệnh hợp lệ:** `"lift_up"` | `"lower_down"` | `"start_cleaning"` | `"stop_cleaning"`
  > **Thứ tự khuyến nghị:** `lift_up` → `start_cleaning` → `stop_cleaning` → `lower_down`

- **Output JSON (Thành công - 202 Accepted):**
  ```json
  {
    "command_id": "cc112233-4455-6677-8899-aabbccddeeff",
    "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
    "command": "lift_up",
    "status": "queued",
    "created_at": "2024-04-24T10:35:00Z"
  }
  ```

### 2.2. Edge device gửi ảnh camera (`POST /api/v1/edge/images`)

- **Input (Headers):** Yêu cầu `X-API-Key: <device_api_key>`
- **Input (Form-data, multipart/form-data):**
  | Field | Type | Mô tả |
  |---|---|---|
  | `device_id` | UUID | ID thiết bị gửi ảnh |
  | `captured_at` | datetime (ISO 8601) | Thời điểm chụp ảnh |
  | `image` | File (JPEG/PNG) | File ảnh, tối đa 5MB |

- **Output JSON (Thành công - 202 Accepted):**
  ```json
  {
    "id": "f1e2d3c4-5678-90ab-cdef-123456789abc",
    "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
    "captured_at": "2024-04-24T10:30:00Z",
    "image_url": "https://storage.example.com/images/ROV_01_20240424T103000Z.jpg",
    "file_size_bytes": 245760,
    "linked_telemetry_time": "2024-04-24T10:30:00Z"
  }
  ```

### 2.3. Edge device gửi telemetry có kèm mức nước (`POST /api/v1/edge/telemetry`)

- **Input (JSON Body - mẫu đầy đủ bao gồm `water_level_raw`):**
  ```json
  {
    "device_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
    "time": "2024-04-24T10:30:00Z",
    "location": "POINT(105.8542 21.0285)",
    "sensors_data": [
      { "sensor_id": "uuid-temperature", "value": 26.5, "quality_flag": 1 },
      { "sensor_id": "uuid-pH", "value": 7.4, "quality_flag": 1 },
      { "sensor_id": "uuid-DO", "value": 6.8, "quality_flag": 1 }
    ],
    "water_level_raw": 18.5
  }
  ```
  > **Ghi chú:** `water_level_raw` là phần trăm mức nước bồn chứa nước ngọt (0–100%). Server sẽ kiểm tra ngưỡng và phát cảnh báo bảo trì nếu cần.

---

## 3. Quy chuẩn Mã lỗi (Error Responses)

Trong FastAPI, nên chuẩn hóa cấu trúc dữ liệu trả về khi gặp lỗi để Frontend (hoặc các hệ thống khác) dễ dàng bóc tách.

**Cấu trúc JSON Lỗi Chuẩn (Standard Error Format):**

```json
{
  "error_code": "CUSTOM_ERROR_CODE",
  "message": "Thông báo lỗi chi tiết dành cho người dùng hoặc developer.",
  "details": null
}
```

_(Trong đó `details` có thể chứa mảng các lỗi validation nếu có)._

### Bảng Mã Lỗi (HTTP Status Codes & Custom Codes)

| HTTP Status                   | Custom `error_code`       | Ngữ cảnh sử dụng (Áp dụng cho API nào)                 | Mô tả chi tiết nguyên nhân lỗi                                                                                  |
| :---------------------------- | :------------------------ | :----------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| **400 Bad Request**           | `INVALID_REQUEST`         | Tất cả các API                                         | Dữ liệu gửi lên không đúng logic nghiệp vụ hoặc bị thiếu thông tin quan trọng.                                  |
| **400 Bad Request**           | `INVALID_COMMAND`         | `POST /actuators/commands`                             | Giá trị `command` không thuộc danh sách hợp lệ (`lift_up`, `lower_down`, `start_cleaning`, `stop_cleaning`).    |
| **400 Bad Request**           | `IMAGE_TOO_LARGE`         | `POST /edge/images`                                    | File ảnh vượt quá kích thước tối đa cho phép (5MB).                                                             |
| **400 Bad Request**           | `INVALID_IMAGE_FORMAT`    | `POST /edge/images`                                    | File ảnh không đúng định dạng JPEG hoặc PNG.                                                                    |
| **400 Bad Request**           | `PASSWORD_MISMATCH`       | `PUT /password`, `POST /reset-password`                | Mật khẩu cũ không khớp hoặc xác nhận mật khẩu mới bị sai.                                                       |
| **401 Unauthorized**          | `UNAUTHORIZED`            | Các API yêu cầu đăng nhập                              | Chưa gửi kèm JWT token, token đã hết hạn, hoặc token không hợp lệ.                                              |
| **401 Unauthorized**          | `INVALID_CREDENTIALS`     | `POST /login`                                          | Người dùng nhập sai Tên đăng nhập (Username) hoặc Mật khẩu.                                                     |
| **401 Unauthorized**          | `INVALID_API_KEY`         | Các API thuộc `/api/v1/edge/*`                         | Edge device gửi sai hoặc thiếu API Key trong header `X-API-Key`.                                                |
| **403 Forbidden**             | `PERMISSION_DENIED`       | Các API thuộc `/api/v1/admin/*`, `/api/v1/actuators/*` | User thường cố gắng gọi API bắt buộc phải có quyền Admin.                                                       |
| **404 Not Found**             | `USER_NOT_FOUND`          | `GET /users/{id}`, `POST /forgot-password`             | Không tìm thấy tài khoản tương ứng trong cơ sở dữ liệu.                                                         |
| **404 Not Found**             | `DEVICE_NOT_FOUND`        | Các API thao tác với thiết bị                          | ID thiết bị truyền lên không tồn tại trong hệ thống.                                                            |
| **404 Not Found**             | `COMMAND_NOT_FOUND`       | `PATCH /edge/commands/{command_id}/ack`                | Command ID không tồn tại hoặc không thuộc thiết bị hiện tại.                                                    |
| **409 Conflict**              | `USERNAME_ALREADY_EXISTS` | `POST /admin/users`                                    | Tên đăng nhập muốn đăng ký/tạo mới đã tồn tại trong hệ thống.                                                   |
| **409 Conflict**              | `PHONE_ALREADY_EXISTS`    | `PUT /users/me/phone`                                  | Số điện thoại muốn cập nhật đã được một tài khoản khác sử dụng.                                                 |
| **409 Conflict**              | `COMMAND_ALREADY_QUEUED`  | `POST /actuators/commands`                             | Thiết bị đã có lệnh cùng loại đang chờ xử lý (status = 'queued'). Tránh gửi lệnh trùng lặp.                     |
| **422 Unprocessable Entity**  | `VALIDATION_ERROR`        | Tất cả các API (Tự động bởi FastAPI/Pydantic)          | Sai định dạng dữ liệu truyền vào (Ví dụ: truyền chuỗi vào trường số nguyên, sai format UUID).                   |
| **500 Internal Server Error** | `INTERNAL_SERVER_ERROR`   | Tất cả các API                                         | Lỗi xuất phát từ phía Server (Lỗi code không mong muốn, đứt kết nối Database, lỗi upload ảnh lên Storage, v.v). |
| **503 Service Unavailable**   | `STORAGE_UNAVAILABLE`     | `POST /edge/images`                                    | Object Storage (S3/Viettel) không phản hồi, không thể lưu ảnh.                                                  |

### Ví dụ lỗi thực tế (422 Validation Error)

Khi người dùng truyền thiếu trường `username` khi gọi API `/login`, FastAPI sẽ tự động trả về:

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

_(Bạn có thể viết một custom exception handler trong FastAPI để map cấu trúc mặc định này về cấu trúc Standard Error Format ở trên)._

### Ví dụ lỗi lệnh không hợp lệ (400 INVALID_COMMAND)

Khi Admin truyền `command` không nằm trong danh sách cho phép:

```json
{
  "error_code": "INVALID_COMMAND",
  "message": "Lệnh 'spin_around' không hợp lệ. Các lệnh được chấp nhận: lift_up, lower_down, start_cleaning, stop_cleaning.",
  "details": null
}
```
