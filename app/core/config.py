import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Robot Telemetry System")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 8)
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./robot_poc.db")
    
    SMS_API_KEY: Optional[str] = os.getenv("SMS_API_KEY", None)
    
    class Config:
        env_file = ".env"

settings = Settings()
