import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.actuator_command import ActuatorCommand

class ActuatorService:
    @staticmethod
    def get_queued_commands(db: Session, device_id: uuid.UUID) -> List[ActuatorCommand]:
        return db.query(ActuatorCommand).filter(
            ActuatorCommand.device_id == device_id,
            ActuatorCommand.status == "queued"
        ).all()

    @staticmethod
    def acknowledge_command(db: Session, command_id: uuid.UUID) -> ActuatorCommand:
        command = db.query(ActuatorCommand).filter(ActuatorCommand.id == command_id).first()
        if not command:
            return None
        command.status = "ack"
        db.commit()
        db.refresh(command)
        return command

actuator_service = ActuatorService()
