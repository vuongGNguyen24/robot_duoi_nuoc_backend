from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.api.v1.dependencies.dependencies import get_db
from app.schemas.user import UserResponse, UserCreate
from app.models.user import User
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
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
        role=payload.role,
        phone_number=payload.phone_number,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
