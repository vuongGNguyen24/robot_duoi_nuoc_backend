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
from datetime import datetime
router = APIRouter()

@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).filter(Device.is_locked == False).all()
    return devices

@router.get("/devices/{device_id}", response_model=DeviceDetailResponse)
async def get_device(device_id: UUID4, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.is_locked == False).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Manual load sensors
    sensors = db.query(Sensor).filter(Sensor.device_id == device_id).all()
    
    # Convert to response model (SQLAlchemy objects to Pydantic works automatically if attributes match)
    # But since DeviceDetail      Response expects 'sensors', we can just set it on the object or return a dict
    device_data = {
        "id": device.id,
        "name": device.name,
        "device_type": device.device_type,
        "firmware_version": device.firmware_version,
        "location": device.location,
        "installed_at": device.installed_at,
        "created_at": device.created_at,
        "sensors": sensors
    }
    return device_data

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    new_device = Device(
        name=payload.name,
        device_type=payload.device_type,
        firmware_version=payload.firmware_version,
        location=payload.location,
        installed_at=payload.installed_at if payload.installed_at else datetime.now(),
        is_locked=False
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.post("/sensor", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(payload: SensorCreate, db: Session = Depends(get_db)):
    # Check if device exists if device_id is provided
    if payload.device_id:
        device = db.query(Device).filter(Device.id == payload.device_id, Device.is_locked == False).first()
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


@router.delete("/devices/{device_id}", status_code=status.HTTP_200_OK)
async def delete_device(device_id: UUID4, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.is_locked = True
    device.locked_at = datetime.now()
    db.commit()
    return device

@router.delete("/sensor/{sensor_id}", status_code=status.HTTP_200_OK)
async def delete_sensor(sensor_id: UUID4, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    sensor.locked_at = datetime.now()
    db.commit()
    return sensor

