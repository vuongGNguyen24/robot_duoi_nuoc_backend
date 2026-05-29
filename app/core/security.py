from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from uuid import UUID
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], role: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "role": role}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


import secrets
import hashlib
class APIKeyHasher:
    @staticmethod
    def generate_salt() -> str:
        """Sinh ra salt khi tạo thiết bị mới"""
        salt = secrets.token_hex(16)
        return salt
    
    @staticmethod
    def generate_api_key() -> str:
        """Sinh ra API Key"""
        return secrets.token_hex(32)
    @staticmethod
    def hash_key(api_key: str, salt: str) -> str:
        """Băm API Key bằng SHA-256 kèm Salt"""
        hash_target = f"{api_key}{salt}".encode('utf-8')
        return hashlib.sha256(hash_target).hexdigest()

    @staticmethod
    def verify_key(provided_key: str, stored_hash: str, salt: str) -> bool:
        """Kiểm tra xem API Key gửi lên có khớp với DB không (An toàn chống Timing Attack)"""
        print(provided_key)
        print(stored_hash)
        print(salt)
        current_hash = APIKeyHasher.hash_key(provided_key, salt)
        # Sử dụng compare_digest để chống tấn công phân tích thời gian phản hồi
        return secrets.compare_digest(current_hash, stored_hash)
    
    