import uuid
from typing import List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, Role, Permission
from app.core.config import settings
from jose import jwt, JWTError
from app.models.device import DeviceManagementLog
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/swagger-login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
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
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_user_roles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> List[str]:
    user_id = current_user.id
    roles = db.query(Permission.name).join(
        Role, Role.permission_id == Permission.id
    ).filter(
        Role.user_id == user_id
    ).all()
    return [r[0] for r in roles]

def require_admin_role(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return require_role("admin", current_user, db)

def require_moderator_role(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return require_role("moderator", current_user, db)
    
def require_role(role: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    roles = get_user_roles(current_user, db)
    if role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def verify_device_api_key(x_api_key: str = Header(...)):
    # Mocking device API key verification for PoC
    if x_api_key != "secret-device-key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return x_api_key

def validate_user_device_ownership(device_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.id
    if not require_role("user", current_user, db):
        return
    
    #get_current_ownership
    device_ids = db.query(DeviceManagementLog.device_id).filter(DeviceManagementLog.user_id == user_id).filter(DeviceManagementLog.removed_at == None).all()
    if not device_ids or device_id not in device_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges")
    return device_id
    

def validate_user_ownership(user_id: uuid.UUID, device_id: uuid.UUID, db: Session):
    device_ids = db.query(DeviceManagementLog.device_id).filter(
        DeviceManagementLog.user_id == user_id
    ).filter(
        DeviceManagementLog.removed_at == None
    ).all()
    if not device_ids or device_id not in [d[0] for d in device_ids]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges")


        
    