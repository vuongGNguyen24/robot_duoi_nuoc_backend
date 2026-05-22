from app.core.database import engine, Base
from app.models.user import User, Permission, Role
from app.models.device import Device
from app.models.telemetry import Sensor, DevicePosition, Telemetry
from app.models.camera_image import CameraImage, ImageAnalysis
from app.models.actuator_command import ActuatorCommand
from app.core.security import get_password_hash
from sqlalchemy.orm import Session
import uuid

def init_db():
    print("Creating tables...")
    # For SQLite compatibility with Geography type (mocking it as String for testing)
    if engine.url.drivername == 'sqlite':
        from sqlalchemy import String
        from geoalchemy2 import Geography
        # This is a bit hacky but works for PoC testing on SQLite
        for table in Base.metadata.tables.values():
            for column in table.columns:
                if isinstance(column.type, Geography):
                    column.type = String()
    
    Base.metadata.create_all(bind=engine)
    
    # Create an initial admin user
    db = Session(engine)
    
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        
        print("Creating permissions...")
        admin_role = Permission(
            id=uuid.uuid4(),
            name="admin",
            description="Admin role"
        )
        user_role = Permission(
            id=uuid.uuid4(),
            name="user",
            description="User role"
        )
        moderator_role = Permission(
            id=uuid.uuid4(),
            name="moderator",
            description="Moderator role"
        )
        db.add(admin_role)
        db.add(user_role)
        db.add(moderator_role)
        db.commit()
        print("Creating admin user...")
        admin = User(
            id=uuid.uuid4(),
            username="admin",
            password_hash=get_password_hash("admin123"),
            phone_number="0123456789"
        )
        user = User(
            id=uuid.uuid4(),
            username="user",
            password_hash=get_password_hash("user123"),
            phone_number="0123456780"
        )
        moderator = User(
            id=uuid.uuid4(),
            username="moderator",
            password_hash=get_password_hash("moderator123"),
            phone_number="0123456781"
        )
        db.add(admin)
        db.add(user)
        db.add(moderator)
        db.commit()

        # Add roles to users
        db.add(Role(
            user_id=admin.id,
            permission_id=admin_role.id
        ))
        db.add(Role(
            user_id=user.id,
            permission_id=user_role.id
        ))
        db.add(Role(
            user_id=moderator.id,
            permission_id=moderator_role.id
        ))
        db.commit()
        
        print("Admin user created: admin / admin123")
        print("User user created: user / user123")
        print("Moderator user created: moderator / moderator123")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
