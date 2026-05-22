from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.api.v1.dependencies.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserCreate
from app.models.user import User, Role, Permission
from app.core.security import get_password_hash
import datetime
from uuid import UUID
router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_locked == False).all()
    result = []
    for user in users:
        role_record = db.query(Role).filter(Role.user_id == user.id).first()
        role_name = "user"
        if role_record:
            permission = db.query(Permission).filter(Permission.id == role_record.permission_id).first()
            if permission:
                role_name = permission.name
        if role_name == "admin":
            continue
        result.append(UserResponse(
            id=user.id,
            username=user.username,
            role=role_name,
            phone_number=user.phone_number,
            created_at=user.created_at
        ))
    return result

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if payload.role == "admin":
        raise HTTPException(status_code=400, detail="Admin role is not allowed")
    # Create new user
    new_user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        phone_number=payload.phone_number,
        created_at=datetime.datetime.now(),
        created_by=current_user.id,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # add permission
    permission = db.query(Permission).filter(Permission.name == payload.role).first()
    if not permission:
        # Rollback user creation if role is invalid
        db.delete(new_user)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Role '{payload.role}' not found")

    role = Role(
        user_id=new_user.id,
        permission_id=permission.id,
    )
    db.add(role)
    db.commit()

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=payload.role,
        phone_number=new_user.phone_number,
        created_at=new_user.created_at
    )

@router.delete("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).filter(User.is_locked == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    user.is_locked = True
    db.commit()
    return UserResponse(
        id=user.id,
        username=user.username,
        role="user",
        phone_number=user.phone_number,
        created_at=user.created_at
    )