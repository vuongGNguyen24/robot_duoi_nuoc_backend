from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from pydantic import UUID4
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_db
from app.schemas.device import DeviceResponse, DeviceCreate, DeviceDetailResponse
from app.schemas.sensor import MultiSensorDetailResponse, SensorResponse, SensorCreate, MultiSensorBase, MultiSensorCreate, MultiSensorResponse
from app.services.admin import AdminService

router = APIRouter()

@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(db: Session = Depends(get_db)):
    return AdminService.list_devices(db)

@router.get("/devices/{device_id}", response_model=DeviceDetailResponse)
async def get_device(device_id: UUID4, db: Session = Depends(get_db)):
    device = AdminService.get_device_by_id(db, device_id, is_locked=False)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    multi_sensors = AdminService.get_multi_sensors_by_device_id(db, device_id)
    
    device_data = {
        "id": device.id,
        "name": device.name,
        "device_type": device.device_type,
        "firmware_version": device.firmware_version,
        "location": device.location,
        "installed_at": device.installed_at,
        "created_at": device.created_at,
        "multi_sensors": multi_sensors
    }
    return device_data

@router.get("/multi-sensors", response_model=List[MultiSensorResponse])
async def list_multi_sensors(db: Session = Depends(get_db)):
    return AdminService.list_multi_sensors(db)


@router.get("/multi-sensor/{multi_sensor_id}", response_model=MultiSensorDetailResponse)
async def get_multi_sensor(multi_sensor_id: UUID4, db: Session = Depends(get_db)):
    multi_sensor = AdminService.get_multi_sensor_by_id(db, multi_sensor_id)
    if not multi_sensor:
        raise HTTPException(status_code=404, detail="Multi-sensor not found")
    
    sensors = AdminService.get_sensors_by_multi_sensor_id(db, multi_sensor_id)
    multi_sensor_data = {
        "id": multi_sensor.id,
        "name": multi_sensor.name,
        "device_id": multi_sensor.device_id,
        "product_code": multi_sensor.product_code,
        "vendor": multi_sensor.vendor,
        "description": multi_sensor.description,
        "sensors": sensors
    }
    return multi_sensor_data

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    return AdminService.create_device(db, payload)


@router.post("/multi-sensor", response_model=MultiSensorResponse, status_code=status.HTTP_201_CREATED)
async def create_multi_sensor(payload: MultiSensorCreate, db: Session = Depends(get_db)):
    return AdminService.create_multi_sensor(db, payload)

@router.post("/sensor", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(payload: SensorCreate, db: Session = Depends(get_db)):
    # Check if device exists if device_id is provided
    if payload.multi_sensor_id:
        multi_sensor = AdminService.get_multi_sensor_by_id(db, payload.multi_sensor_id, is_locked=False)
        if not multi_sensor:
            raise HTTPException(status_code=404, detail="Multi-sensor not found")
            
    return AdminService.create_sensor(db, payload)


@router.delete("/devices/{device_id}", status_code=status.HTTP_200_OK)
async def delete_device(device_id: UUID4, db: Session = Depends(get_db)):
    device = AdminService.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return AdminService.lock_device(db, device)

@router.delete("/multi-sensor/{sensor_id}", status_code=status.HTTP_200_OK)
async def delete_multi_sensor(sensor_id: UUID4, db: Session = Depends(get_db)):
    sensor = AdminService.get_multi_sensor_by_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Multi-sensor not found")
    return AdminService.lock_multi_sensor(db, sensor) 

