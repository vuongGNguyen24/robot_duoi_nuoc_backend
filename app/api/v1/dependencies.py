# app/api/dependencies.py
import uuid
from typing import List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User

# Import các tầng Service xử lý SQL (chúng ta sẽ tạo ở phần dưới)
from app.services.user import UserService
from app.services.device import DeviceService 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/swagger-login")

# LÀM SẠCH: Giữ lại hàm tạo Session kết nối DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# LÀM SẠCH: Giải mã token, còn việc tìm User trong DB thì gọi qua UserService
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
        
    # Thay vì tự query SQL, gọi qua Service độc lập
    user = UserService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user

# LÀM SẠCH: Phân quyền gọi qua UserService
def require_role(role: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    roles = UserService.get_user_roles(db, current_user.id)
    if role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def require_admin_role(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    return require_role("admin", current_user, db)

def require_moderator_role(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    return require_role("moderator", current_user, db)

# LÀM SẠCH: Xác thực Edge Device API Key (Đã cập nhật logic kiểm tra SQL qua DeviceService từ câu hỏi trước)
async def verify_device_api_key(
    x_device_id: str = Header(..., alias="X-Device-ID"),
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    device = await DeviceService.verify_api_key(db, x_device_id, x_api_key)
    if not device:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Device ID or API Key")
    return device

# LÀM SẠCH: Dependency kiểm tra quyền sở hữu thiết bị của User
def validate_user_device_ownership(device_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    has_ownership = DeviceService.check_user_ownership(db, user_id=current_user.id, device_id=device_id)
    if not has_ownership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges")
    return device_id