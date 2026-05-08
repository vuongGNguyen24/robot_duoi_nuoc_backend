from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.schemas.telemetry import EdgeTelemetryPayload
from app.models.telemetry import Telemetry, DevicePosition
from app.models.camera_image import CameraImage
from datetime import datetime
import uuid

from app.services.sms_service import sms_service

class TelemetryService:
    async def process_telemetry(self, db: Session, payload: EdgeTelemetryPayload, background_tasks: BackgroundTasks):
        """
        Xử lý dữ liệu telemetry từ thiết bị biên.
        """
        # 1. Lưu vị trí thiết bị nếu có
        if payload.location:
            # location_wkt = payload.location # POINT(lng lat)
            new_position = DevicePosition(
                device_id=payload.device_id,
                time=payload.time,
                location=payload.location
            )
            db.add(new_position)

        # 2. Lưu dữ liệu cảm biến
        for sensor_record in payload.sensors_data:
            new_telemetry = Telemetry(
                sensor_id=sensor_record.get("sensor_id"),
                time=payload.time,
                value=sensor_record.get("value"),
                quality_flag=sensor_record.get("quality_flag", 1),
                ingestion_time=datetime.utcnow()
            )
            db.add(new_telemetry)

        # 3. Kiểm tra ngưỡng và gửi cảnh báo
        # Giả định một số ngưỡng mặc định
        THRESHOLDS = {
            "temperature": 30.0,
            "pH": 8.5,
            "DO": 5.0 # Min DO
        }
        
        for record in payload.sensors_data:
            # Trong thực tế cần map sensor_id sang loại sensor
            # Giả định sensor_record có thêm "type" hoặc tra cứu từ DB
            sensor_type = record.get("type")
            value = record.get("value")
            
            if sensor_type in THRESHOLDS:
                if (sensor_type == "DO" and value < THRESHOLDS[sensor_type]) or \
                   (sensor_type != "DO" and value > THRESHOLDS[sensor_type]):
                    message = f"Cảnh báo: {sensor_type} vượt ngưỡng ({value})"
                    background_tasks.add_task(sms_service.send_alert, "0123456789", message)

        # 4. Kiểm tra mức nước bồn chứa
        if payload.water_level_raw is not None and payload.water_level_raw < 20.0:
            message = f"Cảnh báo: Mức nước bồn chứa thấp ({payload.water_level_raw}%). Cần bổ sung nước ngọt."
            background_tasks.add_task(sms_service.send_alert, "0123456789", message)

        db.commit()
        return True

telemetry_service = TelemetryService()
