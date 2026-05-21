from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_current_user, get_db
from app.schemas.user import UserResponse, UpdatePhoneRequest
from app.schemas.device import ThresholdUpdateRequest
users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user=Depends(get_current_user)):
    return current_user

# @users_router.get("/settings/thresholds", response_model=UserResponse)
# async def get_user_setting(current_user=Depends(get_current_user)):
#     return current_user

@users_router.put("/me/phone", response_model=UserResponse)
async def update_phone_number(payload: UpdatePhoneRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.phone_number = payload.phone_number
    db.commit()
    db.refresh(current_user)
    return current_user

@users_router.put("/settings/thresholds", status_code=status.HTTP_200_OK)
async def update_warning_thresholds(payload: ThresholdUpdateRequest, db: Session = Depends(get_db)):
    # In a real app, we'd update a specific configuration table or device setting
    # For PoC, we just return success
    return {"message": "Thresholds updated", "sensor_id": payload.sensor_id}