# app/services/admin.py
import datetime
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User, Role, Permission
from app.models.device import Device, DeviceManagementLog, ModsDevice
from app.models.telemetry import Sensor, MultiSensor
from app.schemas.user import UserCreate
from app.schemas.device import DeviceCreate
from app.schemas.sensor import SensorCreate, MultiSensorCreate
from app.core.security import APIKeyHasher
class AdminService:
    # --- User Management ---
    @staticmethod
    def list_users(db: Session) -> List[Dict[str, Any]]:
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
            result.append({
                "id": user.id,
                "username": user.username,
                "role": role_name,
                "phone_number": user.phone_number,
                "created_at": user.created_at
            })
        return result

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_permission_by_name(db: Session, role_name: str) -> Permission | None:
        return db.query(Permission).filter(Permission.name == role_name).first()

    @staticmethod
    def create_user(db: Session, payload: UserCreate, created_by: UUID, permission_id: UUID) -> User:
        from app.core.security import get_password_hash
        new_user = User(
            username=payload.username,
            password_hash=get_password_hash(payload.password),
            phone_number=payload.phone_number,
            created_at=datetime.datetime.now(),
            created_by=created_by,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        role = Role(
            user_id=new_user.id,
            permission_id=permission_id,
        )
        db.add(role)
        db.commit()
        return new_user

    @staticmethod
    def delete_user(db: Session, user: User) -> User:
        user.is_locked = True
        db.commit()
        return user

    # --- Device & Sensor Management ---
    @staticmethod
    def list_devices(db: Session) -> List[Device]:
        return db.query(Device).filter(Device.is_locked == False).all()

    @staticmethod
    def list_multi_sensors(db: Session) -> List[MultiSensor]:
        return db.query(MultiSensor).filter(MultiSensor.locked_at == None).all()
    
    @staticmethod
    def get_device_by_id(db: Session, device_id: UUID, is_locked: bool = False) -> Device | None:
        return db.query(Device).filter(Device.id == device_id, Device.is_locked == is_locked).first()
    
    @staticmethod
    def get_multi_sensor_by_id(db: Session, multi_sensor_id: UUID, is_locked: bool = False) -> MultiSensor | None:
        return db.query(MultiSensor).filter(MultiSensor.id == multi_sensor_id, MultiSensor.locked_at != None if is_locked else MultiSensor.locked_at == None).first()

    @staticmethod
    def get_multi_sensors_by_device_id(db: Session, device_id: UUID) -> List[MultiSensor]:
        return db.query(MultiSensor).filter(MultiSensor.device_id == device_id, MultiSensor.locked_at == None).all()

    @staticmethod
    def get_sensors_by_multi_sensor_id(db: Session, multi_sensor_id: UUID) -> List[Sensor]:
        return db.query(Sensor).filter(Sensor.multi_sensor_id == multi_sensor_id).all()

    @staticmethod
    def get_sensor_by_id(db: Session, sensor_id: UUID) -> Sensor | None:
        return db.query(Sensor).filter(Sensor.id == sensor_id).first()
    @staticmethod
    def create_device(db: Session, payload: DeviceCreate) -> Device:
        salt = APIKeyHasher.generate_salt()
        #create a dummy api key, in PoC we use device id for api key
        dummy_api_key = APIKeyHasher.generate_api_key()
        device_api_key_hash = APIKeyHasher.hash_key(dummy_api_key, salt)
        new_device = Device(
            name=payload.name,
            device_type=payload.device_type,
            firmware_version=payload.firmware_version,
            location=payload.location,
            installed_at=payload.installed_at if payload.installed_at else datetime.datetime.now(),
            is_locked=False,
            device_api_key_hash=device_api_key_hash[0],
            salt=salt
        )
        new_device.device_api_key_hash = APIKeyHasher.hash_key(str(new_device.id), salt)
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return new_device

    @staticmethod
    def create_multi_sensor(db: Session, payload: MultiSensorCreate) -> MultiSensor:
        new_multi_sensor = MultiSensor(
            device_id=payload.device_id,
            name=payload.name,
            product_code=payload.product_code,
            vendor=payload.vendor,
            description=payload.description
        )
        db.add(new_multi_sensor)
        db.commit()
        db.refresh(new_multi_sensor)
        return new_multi_sensor

    @staticmethod
    def create_sensor(db: Session, payload: SensorCreate) -> Sensor:
        new_sensor = Sensor(
            description=payload.description,
            multi_sensor_id=payload.multi_sensor_id,
            sensor_type=payload.sensor_type,
            name=payload.name
        )
        db.add(new_sensor)
        db.commit()
        db.refresh(new_sensor)
        return new_sensor

    @staticmethod
    def lock_device(db: Session, device: Device) -> Device:
        device.is_locked = True
        device.locked_at = datetime.datetime.now()
        db.commit()
        return device



    @staticmethod
    def lock_multi_sensor(db: Session, multi_sensor: MultiSensor) -> MultiSensor:
        multi_sensor.locked_at = datetime.datetime.now()
        db.commit()
        return multi_sensor

    # --- Allocations ---
    @staticmethod
    def get_active_user_device_assignment(db: Session, user_id: UUID, device_id: UUID) -> DeviceManagementLog | None:
        return db.query(DeviceManagementLog).filter(
            DeviceManagementLog.user_id == user_id,
            DeviceManagementLog.device_id == device_id,
            DeviceManagementLog.removed_at.is_(None)
        ).first()

    @staticmethod
    def assign_device_to_user(db: Session, user_id: UUID, device_id: UUID, assigned_by: UUID, notes: str | None) -> DeviceManagementLog:
        new_log = DeviceManagementLog(
            user_id=user_id,
            device_id=device_id,
            assigned_by=assigned_by,
            notes=notes
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log

    @staticmethod
    def remove_device_from_user(db: Session, active_log: DeviceManagementLog, removed_by: UUID, notes: str | None) -> None:
        active_log.removed_at = datetime.datetime.now()
        active_log.removed_by = removed_by
        if notes:
            active_log.notes = notes
        db.commit()

    @staticmethod
    def get_active_mod_device_assignment(db: Session, mod_id: UUID, device_id: UUID) -> ModsDevice | None:
        return db.query(ModsDevice).filter(
            ModsDevice.mod_id == mod_id,
            ModsDevice.device_id == device_id,
            ModsDevice.revoked_at.is_(None)
        ).first()

    @staticmethod
    def assign_device_to_moderator(db: Session, mod_id: UUID, device_id: UUID, granted_by: UUID, notes: str | None) -> ModsDevice:
        new_mod_device = ModsDevice(
            mod_id=mod_id,
            device_id=device_id,
            granted_by=granted_by,
            notes=notes
        )
        db.add(new_mod_device)
        db.commit()
        db.refresh(new_mod_device)
        return new_mod_device

    @staticmethod
    def remove_device_from_moderator(db: Session, active_mod_device: ModsDevice, revoked_by: UUID, notes: str | None) -> None:
        active_mod_device.revoked_at = datetime.datetime.now()
        active_mod_device.revoked_by = revoked_by
        if notes:
            active_mod_device.notes = notes
        db.commit()
        
    