# app/services/device.py
import time
import uuid
from typing import Tuple
from sqlalchemy.orm import Session
from app.models.device import DeviceManagementLog, Device
from app.core.security import APIKeyHasher
# Cache dictionary to store verified (device_id, api_key) -> expiry_timestamp
_apiKeyCache = {}
CACHE_TTL_SECONDS = 300  # 5 minutes cache

class DeviceService:
    @staticmethod
    def check_user_ownership(db: Session, user_id: uuid.UUID, device_id: uuid.UUID) -> bool:
        """
        Kiểm tra xem User có đang sở hữu thiết bị này không.
        """
        device_ids = db.query(DeviceManagementLog.device_id).filter(
            DeviceManagementLog.user_id == user_id
        ).filter(
            DeviceManagementLog.removed_at == None
        ).all()
        
        # Trả về True nếu tìm thấy device_id nằm trong danh sách sở hữu
        return device_id in [d[0] for d in device_ids]

    @staticmethod
    async def verify_api_key(db: Session, device_id: str, api_key: str) -> bool:
        """
        Kiểm tra xem Edge Device có hợp lệ không. Sử dụng cache để xác thực nhanh.
        """
        currentTime = time.time()
        cacheKey = (str(device_id), api_key)
        
        # Kiểm tra cache
        if cacheKey in _apiKeyCache:
            expiry = _apiKeyCache[cacheKey]
            if currentTime < expiry:
                return True
            else:
                del _apiKeyCache[cacheKey]
                
        try:
            device_uuid = uuid.UUID(str(device_id))
        except ValueError:
            return False
        salt: Tuple[str] = db.query(Device.salt).filter(
            Device.id == device_uuid
        ).first()
        print(salt)
        print(api_key)
        if salt is None:
            return False
        api_key_hash: Tuple[str] = db.query(Device.device_api_key_hash).filter(
            Device.id == device_uuid
        ).first()
        
        APIKeyHasher.verify_key(api_key, api_key_hash[0], salt[0])
        if api_key_hash is not None:
            # Lưu vào cache
            _apiKeyCache[cacheKey] = currentTime + CACHE_TTL_SECONDS
            return True
            
        return False

    