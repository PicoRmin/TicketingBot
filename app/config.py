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
    REFRESH_TOKEN_SECRET: str = "your-refresh-secret-key-change"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    
    # Security validations for production
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    def validate_production_settings(self):
        """Validate production settings"""
        if self.is_production:
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if self.SECRET_KEY == "your-secret-key-here-change-in-production":
                raise ValueError("SECRET_KEY must be changed in production")
            if self.REFRESH_TOKEN_SECRET == "your-refresh-secret-key-change":
                raise ValueError("REFRESH_TOKEN_SECRET must be changed in production")
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
            if not self.DATABASE_URL or self.DATABASE_URL == "sqlite:///./ticketing.db":
                # SQLite در Production مجاز است اما توصیه نمی‌شود
                pass  # Warning only, not error
            # بررسی Email settings اگر EMAIL_ENABLED=True باشد
            if self.EMAIL_ENABLED:
                if not self.EMAIL_SMTP_HOST or not self.EMAIL_SMTP_USER or not self.EMAIL_SMTP_PASSWORD:
                    raise ValueError("SMTP settings (host, user, password) must be configured if email is enabled in production.")
                if self.EMAIL_SMTP_PORT not in [465, 587]:
                    raise ValueError("EMAIL_SMTP_PORT must be 465 (SSL) or 587 (TLS) in production if email is enabled.")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str | None = None
    TELEGRAM_WEBHOOK_SECRET: str | None = None
    TELEGRAM_ADMIN_GROUP_ID: str | None = None
    TELEGRAM_ADMIN_DAILY_REPORT_ENABLED: bool = False
    TELEGRAM_ADMIN_DAILY_REPORT_HOUR: int = 8
    TELEGRAM_SESSION_TIMEOUT_MINUTES: int = 30  # Session timeout in minutes
    TELEGRAM_SESSION_CLEANUP_INTERVAL_MINUTES: int = 60  # Cleanup interval in minutes
    
    # Email Configuration (SMTP)
    EMAIL_ENABLED: bool = False
    EMAIL_SMTP_HOST: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USER: str = ""
    EMAIL_SMTP_PASSWORD: str = ""
    EMAIL_SMTP_USE_TLS: bool = True
    EMAIL_SMTP_USE_SSL: bool = False
    EMAIL_FROM_ADDRESS: str = "noreply@iranmehr.com"
    EMAIL_FROM_NAME: str = "سیستم تیکتینگ ایرانمهر"
    EMAIL_REPLY_TO: str | None = None
    EMAIL_BCC_ADDRESSES: str | None = None  # Comma-separated list
    
    # Aliases for backward compatibility
    @property
    def SMTP_HOST(self) -> str:
        """Alias for EMAIL_SMTP_HOST"""
        return self.EMAIL_SMTP_HOST
    
    @property
    def SMTP_PORT(self) -> int:
        """Alias for EMAIL_SMTP_PORT"""
        return self.EMAIL_SMTP_PORT
    
    @property
    def SMTP_USERNAME(self) -> str:
        """Alias for EMAIL_SMTP_USER"""
        return self.EMAIL_SMTP_USER
    
    @property
    def SMTP_PASSWORD(self) -> str:
        """Alias for EMAIL_SMTP_PASSWORD"""
        return self.EMAIL_SMTP_PASSWORD
    
    @property
    def SMTP_USE_TLS(self) -> bool:
        """Alias for EMAIL_SMTP_USE_TLS"""
        return self.EMAIL_SMTP_USE_TLS
    
    @property
    def SMTP_USE_SSL(self) -> bool:
        """Alias for EMAIL_SMTP_USE_SSL"""
        return self.EMAIL_SMTP_USE_SSL
    
    @property
    def EMAIL_FROM(self) -> str:
        """Alias for EMAIL_FROM_ADDRESS"""
        return self.EMAIL_FROM_ADDRESS
    
    # CORS - Can be set as comma-separated string in .env file
    # Default includes common development ports for Vite, React, and other frontend frameworks
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8000,http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:8000"

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

