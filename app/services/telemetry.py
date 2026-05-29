from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from typing import List
from app.schemas.telemetry import EdgeTelemetryPayload
from app.models.device import Device, DeviceManagementLog
from app.models.telemetry import Telemetry, DevicePosition, Sensor
from app.models.camera_image import CameraImage
from datetime import datetime
import uuid
import io

from app.services.sms import sms_service

class TelemetryService:
    async def save_edge_telemetry(self, db: Session, payload: EdgeTelemetryPayload, background_tasks: BackgroundTasks):
        """
        Xử lý và lưu dữ liệu telemetry từ thiết bị biên theo EdgeTelemetryPayload schema.
        """
        # 1. Tìm hoặc tạo Sensor
        sensor = db.query(Sensor).filter(
            Sensor.device_id == payload.device_id,
            Sensor.name == payload.sensor_name
        ).first()
        
        if not sensor:
            sensor = Sensor(
                id=uuid.uuid4(),
                name=payload.sensor_name,
                device_id=payload.device_id,
                sensor_type=payload.sensor_name.lower(),
                description=f"Auto-generated sensor for {payload.sensor_name}"
            )
            db.add(sensor)
            db.commit()
            db.refresh(sensor)

        # 2. Tạo bản ghi Telemetry
        new_telemetry = Telemetry(
            id=uuid.uuid4(),
            sensor_id=sensor.id,
            time=payload.time,
            unit=payload.unit,
            value=payload.sensor_value,
            quality_flag=payload.quality_flag if payload.quality_flag is not None else 1
        )
        db.add(new_telemetry)
        
        # 3. Kiểm tra ngưỡng cảnh báo
        THRESHOLDS = {
            "temperature": 30.0,
            "ph": 8.5,
            "do": 5.0  # Min DO
        }
        
        name_lower = payload.sensor_name.lower()
        sensor_type = None
        if "temp" in name_lower or "nhiệt" in name_lower:
            sensor_type = "temperature"
        elif "ph" in name_lower:
            sensor_type = "ph"
        elif "do" in name_lower or "oxy" in name_lower:
            sensor_type = "do"
            
        if sensor_type in THRESHOLDS:
            val = payload.sensor_value
            limit = THRESHOLDS[sensor_type]
            if (sensor_type == "do" and val < limit) or (sensor_type != "do" and val > limit):
                message = f"Cảnh báo: Cảm biến {payload.sensor_name} đạt giá trị {val} {payload.unit} (ngưỡng {limit})"
                background_tasks.add_task(sms_service.send_alert, "0123456789", message)

        db.commit()
        return new_telemetry

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

    def get_dashboard_devices(self, db: Session, user_id: uuid.UUID) -> List[Device]:
        device_ids = db.query(DeviceManagementLog.device_id).filter(
            DeviceManagementLog.user_id == user_id
        ).filter(
            DeviceManagementLog.removed_at == None
        ).all()
        if not device_ids:
            return []
        return db.query(Device).filter(
            Device.id.in_([d[0] for d in device_ids])
        ).filter(
            Device.is_locked == False
        ).all()

    def get_device_by_id(self, db: Session, device_id: uuid.UUID) -> Device | None:
        return db.query(Device).filter(
            Device.id == device_id
        ).filter(
            Device.is_locked == False
        ).first()

    def get_device_summary(self, db: Session, device_id: uuid.UUID):
        sensors = db.query(Sensor).filter(Sensor.device_id == device_id).all()
        latest_sensor_telemetry = []
        for sensor in sensors:
            telemetry = db.query(Telemetry).filter(
                Telemetry.sensor_id == sensor.id
            ).order_by(
                Telemetry.time.desc()
            ).first()
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

    def get_dashboard_telemetry(self, db: Session, device: Device, limit: int):
        device_ids = [device.id]
        device_map = {device.id: device.name}

        raw_telemetry = (
            db.query(Telemetry, Sensor.device_id, Sensor.description)
            .join(Sensor, Telemetry.sensor_id == Sensor.id)
            .filter(Sensor.device_id.in_(device_ids))
            .order_by(Telemetry.time.desc())
            .limit(limit * 5)
            .all()
        )

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
            
            reading_key = sensor_desc.lower().replace(" ", "_") if sensor_desc else "value"
            records_dict[key]["readings"][reading_key] = t.value

        final_records = list(records_dict.values())
        for record in final_records:
            pos = db.query(DevicePosition).filter(
                DevicePosition.device_id == record["device_id"],
                DevicePosition.time <= record["time"]
            ).order_by(DevicePosition.time.desc()).first()
            
            if pos:
                record["location"] = {"lat": 21.0285, "lng": 105.8542}

            img = db.query(CameraImage).filter(
                CameraImage.device_id == record["device_id"],
                CameraImage.captured_at <= record["time"]
            ).order_by(CameraImage.captured_at.desc()).first()
            
            if img:
                record["image_url"] = img.image_url

        return final_records

telemetry_service = TelemetryService()
