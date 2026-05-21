from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from pydantic import UUID4
from sqlalchemy.orm import Session
from app.api.v1.dependencies.dependencies import get_db
from app.schemas.device import DeviceResponse, DeviceCreate, DeviceDetailResponse
from app.models.user import User
from app.models.device import Device
from app.models.telemetry import Sensor
from app.schemas.sensor import SensorResponse, SensorCreate

router = APIRouter()

@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return devices

@router.get("/devices/{device_id}", response_model=DeviceDetailResponse)
async def get_device(device_id: UUID4, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Manual load sensors
    sensors = db.query(Sensor).filter(Sensor.device_id == device_id).all()
    
    # Convert to response model (SQLAlchemy objects to Pydantic works automatically if attributes match)
    # But since DeviceDetailResponse expects 'sensors', we can just set it on the object or return a dict
    device_data = {
        "id": device.id,
        "name": device.name,
        "device_type": device.device_type,
        "firmware_version": device.firmware_version,
        "location": device.location,
        "user_id": device.user_id,
        "installed_at": device.installed_at,
        "created_at": device.created_at,
        "sensors": sensors
    }
    return device_data

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
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

@router.post("/sensor", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(payload: SensorCreate, db: Session = Depends(get_db)):
    # Check if device exists if device_id is provided
    if payload.device_id:
        device = db.query(Device).filter(Device.id == payload.device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
            
    new_sensor = Sensor(
        unit=payload.unit,
        description=payload.description,
        device_id=payload.device_id
    )
    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)
    return new_sensor
