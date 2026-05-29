from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_current_user, get_db
from app.schemas.user import UserResponse, UpdatePhoneRequest
from app.schemas.device import ThresholdUpdateRequest
from app.services.user import UserService
users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    roles = UserService.get_user_roles(db, current_user.id)
    print(roles)
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        phone_number=current_user.phone_number,
        created_at=current_user.created_at,
        role=roles[0]
    )

# @users_router.get("/settings/thresholds", response_model=UserResponse)
# async def get_user_setting(current_user=Depends(get_current_user)):
#     return current_user

from app.services.user import UserService

@users_router.put("/me/phone", response_model=UserResponse)
async def update_phone_number(payload: UpdatePhoneRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    updated_user = UserService.update_phone_number(db, current_user, payload.phone_number)
    return updated_user

@users_router.put("/settings/thresholds", status_code=status.HTTP_200_OK)
async def update_warning_thresholds(payload: ThresholdUpdateRequest, db: Session = Depends(get_db)):
    # In a real app, we'd update a specific configuration table or device setting
    # For PoC, we just return success
    return {"message": "Thresholds updated", "sensor_id": payload.sensor_id}