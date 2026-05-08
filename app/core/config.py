from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Robot Telemetry System"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    DATABASE_URL: str = "sqlite:///./robot_poc.db"
    
    SMS_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
