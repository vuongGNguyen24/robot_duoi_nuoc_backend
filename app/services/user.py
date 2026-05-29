# app/services/user.py
import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User, Role, Permission

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_roles(db: Session, user_id: uuid.UUID) -> List[str]:
        # Bốc đoạn code join phức tạp từ dependency cũ về đây
        roles = db.query(Permission.name).join(
            Role, Role.permission_id == Permission.id
        ).filter(
            Role.user_id == user_id
        ).all()
        return [r[0] for r in roles]

    @staticmethod
    def update_phone_number(db: Session, user: User, phone_number: str) -> User:
        user.phone_number = phone_number
        db.commit()
        db.refresh(user)
        return user