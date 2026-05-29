# app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models.user import User, Role, Permission
from app.core.security import get_password_hash, pwd_context
from typing import List

class AuthService:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_phone_number(db: Session, phone_number: str) -> User | None:
        return db.query(User).filter(User.phone_number == phone_number).first()

    @staticmethod
    def get_user_roles(db: Session, user_id) -> List[str]:
        roles = db.query(Permission.name).join(
            Role, Role.permission_id == Permission.id
        ).filter(
            Role.user_id == user_id
        ).all()
        return [r[0] for r in roles]

    @staticmethod
    def change_password(db: Session, user: User, new_password: str) -> None:
        user.password_hash = get_password_hash(new_password)
        db.commit()

    @staticmethod
    def reset_password(db: Session, user: User, new_password: str) -> None:
        user.password_hash = pwd_context.hash(new_password)
        db.commit()
