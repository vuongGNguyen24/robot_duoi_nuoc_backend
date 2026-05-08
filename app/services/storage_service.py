import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.camera_image import CameraImage

class StorageService:
    async def save_camera_image(self, db: Session, device_id: uuid.UUID, captured_at: datetime, image_file):
        """
        Lưu ảnh camera vào hệ thống lưu trữ (Mock) và ghi log vào DB.
        """
        # 1. Upload logic (giả lập lưu vào thư mục local)
        file_extension = image_file.content_type.split("/")[-1]
        filename = f"{device_id}_{captured_at.strftime('%Y%m%dT%H%M%SZ')}.{file_extension}"
        
        # Trong thực tế sẽ upload lên S3/Viettel Cloud
        image_url = f"https://storage.example.com/images/{filename}"
        
        # 2. Lưu vào database
        new_image = CameraImage(
            id=uuid.uuid4(),
            device_id=device_id,
            captured_at=captured_at,
            image_url=image_url,
            file_size=0, # Giả lập kích thước
            width=None,
            height=None
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        
        return {
            "id": new_image.id,
            "device_id": new_image.device_id,
            "captured_at": new_image.captured_at,
            "image_url": new_image.image_url,
            "file_size_bytes": new_image.file_size,
            "linked_telemetry_time": new_image.captured_at
        }

storage_service = StorageService()
