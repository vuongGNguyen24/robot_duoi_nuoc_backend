from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.schemas import LoginRequest, TokenResponse, ChangePasswordRequest, SendOtpRequest, VerifyOtpRequest
from app.models.user import User
from app.core.security import verify_password, create_access_token, pwd_context, get_password_hash

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.id, role=user.role)
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


@auth_router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(payload: ChangePasswordRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return None

@auth_router.post("/send-otp", status_code=status.HTTP_202_ACCEPTED)
async def send_otp(payload: SendOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Mock sending SMS
    return {"message": "OTP sent", "otp_code": "123456"}


@auth_router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    # Mock verify OTP
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.otp != "123456":
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"message": "OTP verified successfully"}

@auth_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    #generate random password
    def generate_password():
        import random
        tmp = random.randint(0, 10 ** 6)
        new_password = f"@{random.choice(['!','@'])}{random.choice([chr(ord('a') + c) for c in range(26)])}{random.choice([chr(ord('A') + c) for c in range(26)])}{tmp:6d}"
        return new_password
    new_password = "abc123!@#"
    user.password_hash = pwd_context.hash(new_password)
    db.commit()
    return {"message": "Password reset successful", "new_password": new_password}




