from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.api.dependencies import require_admin_role, get_db
from app.schemas.user import UserResponse, UserCreate
from app.schemas.device import DeviceResponse, DeviceCreate
from app.models.user import User
from app.models.device import Device
from app.core.security import get_password_hash

admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin_role)])

@admin_router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@admin_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    new_user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        phone_number=payload.phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@admin_router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return devices

@admin_router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    # Check if user exists if user_id is provided
    if payload.user_id:
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
    new_device = Device(
        name=payload.name,
        device_type=payload.device_type,
        firmware_version=payload.firmware_version,
        location=payload.location,
        user_id=payload.user_id
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


