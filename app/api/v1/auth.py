from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_db, get_current_user
from app.schemas import LoginRequest, TokenResponse, ChangePasswordRequest, SendOtpRequest, VerifyOtpRequest
from app.core.security import verify_password, create_access_token
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


# 1. Endpoint phụ này phục vụ RIÊNG cho Swagger điền Form data
@auth_router.post("/swagger-login") # bao che giấu khỏi docs cho đỡ rối
async def swagger_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Lấy username và password từ Form data mà Swagger gửi lên
    username = form_data.username
    password = form_data.password
    
    user = AuthService.get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = user.id
    roles = AuthService.get_user_roles(db, user_id) 
    role = roles[0]
    #TODO: create token with all roles
    access_token = create_access_token(subject=user.id, role=role)
    return {"access_token": access_token, "token_type": "bearer", "role": role}
        

@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_username(db, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = user.id
    roles = AuthService.get_user_roles(db, user_id) 
    role = roles[0]
    #TODO: create token with all roles
    access_token = create_access_token(subject=user.id, role=role)
    return {"access_token": access_token, "token_type": "bearer", "role": role}


@auth_router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(payload: ChangePasswordRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    AuthService.change_password(db, current_user, payload.new_password)
    return None

@auth_router.post("/send-otp", status_code=status.HTTP_202_ACCEPTED)
async def send_otp(payload: SendOtpRequest, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_phone_number(db, payload.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Mock sending SMS
    return {"message": "OTP sent", "otp_code": "123456"}


@auth_router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    # Mock verify OTP
    user = AuthService.get_user_by_phone_number(db, payload.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.otp != "123456":
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"message": "OTP verified successfully"}

@auth_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_phone_number(db, payload.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    #generate random password
    def generate_password():
        import random
        tmp = random.randint(0, 10 ** 6)
        new_password = f"@{random.choice(['!','@'])}{random.choice([chr(ord('a') + c) for c in range(26)])}{random.choice([chr(ord('A') + c) for c in range(26)])}{tmp:6d}"
        return new_password
    new_password = "abc123!@#"
    AuthService.reset_password(db, user, new_password)
    return {"message": "Password reset successful", "new_password": new_password}




