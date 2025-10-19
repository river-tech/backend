from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://usitech_user:1234@localhost:6969/usitech"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "USITech Backend"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Email Configuration
    MAIL_USERNAME: str = "usitechf4@gmail.com"
    MAIL_PASSWORD: str = "mhnqcrhsoitzcwee"
    MAIL_FROM: str = "usitechf4@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
