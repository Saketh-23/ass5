import os
from pydantic import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "ConnectFit"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./connectfit.db"
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-token-generation")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:4200", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()