from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.api.v1.dependencies.dependencies import get_db, get_current_user
from app.schemas.device import (
    UserDeviceAssignment, UserDeviceRemoval, ModDeviceAssignment, ModDeviceRemoval
)
from app.models.user import User
from app.models.device import Device, DeviceManagementLog, ModsDevice

router = APIRouter()

# --- Device Allocation (Users) ---
@router.post("/users/devices", status_code=status.HTTP_201_CREATED)
async def assign_device_to_user(
    payload: UserDeviceAssignment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(User).filter(User.id == payload.user_id).filter(User.is_locked == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify device exists
    device = db.query(Device).filter(Device.id == payload.device_id).filter(Device.is_locked == False).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Check active assignment
    active_log = db.query(DeviceManagementLog).filter(
        DeviceManagementLog.user_id == payload.user_id,
        DeviceManagementLog.device_id == payload.device_id,
        DeviceManagementLog.removed_at.is_(None)
    ).first()
    if active_log:
        raise HTTPException(status_code=400, detail="Device is already assigned to this user")
        
    new_log = DeviceManagementLog(
        user_id=payload.user_id,
        device_id=payload.device_id,
        assigned_by=current_user.id,
        notes=payload.notes
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return {"message": "Device successfully assigned to user", "log_id": str(new_log.id)}

@router.delete("/users/devices", status_code=status.HTTP_200_OK)
async def remove_device_from_user(
    payload: UserDeviceRemoval,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find active assignment
    active_log = db.query(DeviceManagementLog).filter(
        DeviceManagementLog.user_id == payload.user_id,
        DeviceManagementLog.device_id == payload.device_id,
        DeviceManagementLog.removed_at.is_(None)
    ).first()
    if not active_log:
        raise HTTPException(status_code=404, detail="Active assignment not found")
        
    active_log.removed_at = datetime.now()
    active_log.removed_by = current_user.id
    if payload.notes:
        active_log.notes = payload.notes
        
    db.commit()
    return {"message": "Device successfully removed from user"}

# --- Device Allocation (Moderators) ---
@router.post("/moderators/devices", status_code=status.HTTP_201_CREATED)
async def assign_device_to_moderator(
    payload: ModDeviceAssignment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify moderator exists
    moderator = db.query(User).filter(User.id == payload.mod_id).first()
    if not moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")
        
    # Verify device exists
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Check active assignment
    active_mod_device = db.query(ModsDevice).filter(
        ModsDevice.mod_id == payload.mod_id,
        ModsDevice.device_id == payload.device_id,
        ModsDevice.revoked_at.is_(None)
    ).first()
    if active_mod_device:
        raise HTTPException(status_code=400, detail="Device is already assigned to this moderator")
        
    new_mod_device = ModsDevice(
        mod_id=payload.mod_id,
        device_id=payload.device_id,
        granted_by=current_user.id,
        notes=payload.notes
    )
    db.add(new_mod_device)
    db.commit()
    db.refresh(new_mod_device)
    return {"message": "Device successfully assigned to moderator", "log_id": str(new_mod_device.id)}

@router.delete("/moderators/devices", status_code=status.HTTP_200_OK)
async def remove_device_from_moderator(
    payload: ModDeviceRemoval,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find active assignment
    active_mod_device = db.query(ModsDevice).filter(
        ModsDevice.mod_id == payload.mod_id,
        ModsDevice.device_id == payload.device_id,
        ModsDevice.revoked_at.is_(None)
    ).first()
    if not active_mod_device:
        raise HTTPException(status_code=404, detail="Active assignment not found")
        
    active_mod_device.revoked_at = datetime.now()
    active_mod_device.revoked_by = current_user.id
    if payload.notes:
        active_mod_device.notes = payload.notes
        
    db.commit()
    return {"message": "Device successfully removed from moderator"}
