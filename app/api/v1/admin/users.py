from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserCreate
from app.models.user import User
from app.services.admin import AdminService
from app.services.user import UserService
from uuid import UUID

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users_data = AdminService.list_users(db)
    return [UserResponse(**u) for u in users_data]

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if user already exists
    existing_user = AdminService.get_user_by_username(db, payload.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if payload.role == "admin":
        raise HTTPException(status_code=400, detail="Admin role is not allowed")
        
    # get permission
    permission = AdminService.get_permission_by_name(db, payload.role)
    if not permission:
        raise HTTPException(status_code=400, detail=f"Role '{payload.role}' not found")

    new_user = AdminService.create_user(db, payload, current_user.id, permission.id)
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=payload.role,
        phone_number=new_user.phone_number,
        created_at=new_user.created_at
    )

@router.delete("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = UserService.get_user_by_id(db, user_id)
    if not user or user.is_locked:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    AdminService.delete_user(db, user)
    return UserResponse(
        id=user.id,
        username=user.username,
        role="user",
        phone_number=user.phone_number,
        created_at=user.created_at
    )