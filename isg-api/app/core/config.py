import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "ISG Safety API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Occupational Safety Management System API"
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database
    DATABASE_URL: str = "postgresql://isg_user:isg_password@localhost/isg_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            # Include alternate Vite port when 5173 is busy
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            # Production domains
            "https://safevisor.navitser.online",
            "https://api.navitser.online",
        ]
    )
    
    # Security
    BCRYPT_SCHEMES: list[str] = ["argon2", "bcrypt"]
    BCRYPT_DEPRECATED: str = "auto"
    USE_HTTPS: bool = False  # Set to True in production
    COOKIE_SECURE: bool = False  # Set to True in production (requires HTTPS)
    COOKIE_SAMESITE: str = "lax"  # lax, strict, or none
    COOKIE_DOMAIN: str | None = None  # Set to your domain in production
    
    # Feature flags (can be enabled in production if required)
    # When True, camera streaming/detection endpoints do not require auth
    RELAX_CAMERA_AUTH: bool = False
    # When True, allow refresh to succeed even if DB record for refresh token is missing (JWT still must be valid)
    RELAX_REFRESH_DB_MISS: bool = False
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    LOGIN_RATE_LIMIT: str = "5/minute"  # 5 login attempts per minute per IP
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_UPLOAD_EXTENSIONS: list[str] = Field(
        default_factory=lambda: [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    )
    
    # Admin user (for initial setup)
    FIRST_SUPERUSER_EMAIL: str = "admin@isg.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []

            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except json.JSONDecodeError:
                    pass

            return [origin.strip() for origin in value.split(",") if origin.strip()]

        if isinstance(value, (list, tuple, set)):
            cleaned = []
            for origin in value:
                if origin is None:
                    continue
                origin_str = str(origin).strip()
                if origin_str:
                    cleaned.append(origin_str)
            return cleaned

        return []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()