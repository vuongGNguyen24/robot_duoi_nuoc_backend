from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from typing import List
from app.schemas.telemetry import EdgeTelemetryPayload
from app.models.device import Device
from app.models.telemetry import Telemetry, DevicePosition, Sensor
from app.models.camera_image import CameraImage
from datetime import datetime
import uuid
import io

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

    async def export_telemetry_data(self, db: Session, device_id: uuid.UUID, start_date: datetime, end_date: datetime, columns: List[str], format: str):
        """
        Xuất dữ liệu telemetry ra file CSV hoặc XLSX.
        """
        from typing import List
        import pandas as pd
        
        device = db.query(Device).filter(Device.id == device_id).first()
            
        device_ids = [device.id]
        device_map = {device.id: device.name}
        
        # 2. Truy vấn dữ liệu Telemetry kèm thông tin Sensor
        raw_telemetry = (
            db.query(Telemetry, Sensor.device_id, Sensor.description)
            .join(Sensor, Telemetry.sensor_id == Sensor.id)
            .filter(Sensor.device_id.in_(device_ids))
            .filter(Telemetry.time >= start_date)
            .filter(Telemetry.time <= end_date)
            .order_by(Telemetry.time.desc())
            .all()
        )
        
        if not raw_telemetry:
            # Tạo DF trống với các cột yêu cầu để trả về file trắng thay vì error
            df = pd.DataFrame(columns=["time", "device_name"] + columns)
        else:
            # 3. Gom nhóm dữ liệu theo (device_id, time)
            records_dict = {}
            for t, device_id, sensor_desc in raw_telemetry:
                key = (device_id, t.time)
                if key not in records_dict:
                    records_dict[key] = {
                        "time": t.time,
                        "device_name": device_map.get(device_id)
                    }
                
                # Format key cho readings đồng bộ với Dashboard
                reading_key = sensor_desc.lower().replace(" ", "_") if sensor_desc else "value"
                records_dict[key][reading_key] = t.value
            
            df = pd.DataFrame(list(records_dict.values()))
            
            # Lọc các cột người dùng yêu cầu + các cột mặc định
            available_cols = ["time", "device_name"]
            for col in columns:
                if col in df.columns:
                    available_cols.append(col)
            
            df = df[available_cols]

        # 4. Tạo file stream
        output = io.BytesIO()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "xlsx":
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Telemetry Report")
            filename = f"report_{timestamp}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            df.to_csv(output, index=False, encoding="utf-8-sig")
            filename = f"report_{timestamp}.csv"
            media_type = "text/csv"
            
        output.seek(0)
        return output, filename, media_type

telemetry_service = TelemetryService()
