from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "ISG Safety API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Occupational Safety Management System API"
    
    # Database
    DATABASE_URL: str = "postgresql://isg_user:isg_password@localhost/isg_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Include alternate Vite port when 5173 is busy
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # Security
    BCRYPT_SCHEMES: list = ["argon2", "bcrypt"]
    BCRYPT_DEPRECATED: str = "auto"
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Admin user (for initial setup)
    FIRST_SUPERUSER_EMAIL: str = "admin@isg.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()