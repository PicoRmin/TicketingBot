"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Iranmehr Ticketing System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./ticketing.db"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str | None = None
    TELEGRAM_WEBHOOK_SECRET: str | None = None
    
    # CORS - Can be set as comma-separated string in .env file
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8000,http://localhost:5173,http://127.0.0.1:5173"

    # External integration base URLs
    API_BASE_URL: str = "http://127.0.0.1:8000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list"""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Also add localhost variants for common ports
        additional_origins = []
        for origin in origins:
            if "localhost" in origin:
                # Add 127.0.0.1 variant
                additional_origins.append(origin.replace("localhost", "127.0.0.1"))
            elif "127.0.0.1" in origin:
                # Add localhost variant
                additional_origins.append(origin.replace("127.0.0.1", "localhost"))
        # Combine and remove duplicates
        all_origins = list(set(origins + additional_origins))
        return all_origins

    # Logging
    LOG_LEVEL: str = "DEBUG"  # Changed to DEBUG for better error tracking
    LOG_FILE: str = "logs/app.log"

    # File Storage
    UPLOAD_DIR: Path = Path("storage/uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

