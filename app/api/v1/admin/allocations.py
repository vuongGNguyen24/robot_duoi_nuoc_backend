from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_db, get_current_user
from app.schemas.device import (
    UserDeviceAssignment, UserDeviceRemoval, ModDeviceAssignment, ModDeviceRemoval
)
from app.models.user import User
from app.services.admin import AdminService

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
    device = AdminService.get_device_by_id(db, payload.device_id, is_locked=False)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Check active assignment
    active_log = AdminService.get_active_user_device_assignment(db, payload.user_id, payload.device_id)
    if active_log:
        raise HTTPException(status_code=400, detail="Device is already assigned to this user")
        
    new_log = AdminService.assign_device_to_user(
        db, payload.user_id, payload.device_id, current_user.id, payload.notes
    )
    return {"message": "Device successfully assigned to user", "log_id": str(new_log.id)}

@router.delete("/users/devices", status_code=status.HTTP_200_OK)
async def remove_device_from_user(
    payload: UserDeviceRemoval,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find active assignment
    active_log = AdminService.get_active_user_device_assignment(db, payload.user_id, payload.device_id)
    if not active_log:
        raise HTTPException(status_code=404, detail="Active assignment not found")
        
    AdminService.remove_device_from_user(db, active_log, current_user.id, payload.notes)
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
    device = AdminService.get_device_by_id(db, payload.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Check active assignment
    active_mod_device = AdminService.get_active_mod_device_assignment(db, payload.mod_id, payload.device_id)
    if active_mod_device:
        raise HTTPException(status_code=400, detail="Device is already assigned to this moderator")
        
    new_mod_device = AdminService.assign_device_to_moderator(
        db, payload.mod_id, payload.device_id, current_user.id, payload.notes
    )
    return {"message": "Device successfully assigned to moderator", "log_id": str(new_mod_device.id)}

@router.delete("/moderators/devices", status_code=status.HTTP_200_OK)
async def remove_device_from_moderator(
    payload: ModDeviceRemoval,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find active assignment
    active_mod_device = AdminService.get_active_mod_device_assignment(db, payload.mod_id, payload.device_id)
    if not active_mod_device:
        raise HTTPException(status_code=404, detail="Active assignment not found")
        
    AdminService.remove_device_from_moderator(db, active_mod_device, current_user.id, payload.notes)
    return {"message": "Device successfully removed from moderator"}
