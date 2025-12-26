"""Application configuration and settings."""

from zoneinfo import ZoneInfo
from environs import Env
from pathlib import Path
from typing import List

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Application settings and configuration."""

    def __init__(self):
        # Base Directory
        self.BASE_DIR = BASE_DIR

        # Timezone
        self.TIMEZONE = ZoneInfo(env.str("TIMEZONE", default="Asia/Tashkent"))

        # JWT Settings
        self.JWT_SECRET_KEY = env.str(
            "JWT_SECRET_KEY", default=env.str("SECRET_KEY", default="")
        )
        self.JWT_ALGORITHM = env.str("JWT_ALGORITHM", default="HS256")
        self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = env.int(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=30
        )
        self.JWT_REFRESH_TOKEN_EXPIRE_DAYS = env.int(
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS", default=7
        )

        # Cookie Settings
        self.COOKIE_SECURE = env.bool(
            "COOKIE_SECURE", default=False
        )  # True in production
        self.COOKIE_HTTPONLY = True
        self.COOKIE_SAMESITE = env.str(
            "COOKIE_SAMESITE", default="lax"
        )  # "lax", "strict", or "none"
        self.COOKIE_DOMAIN = env.str("COOKIE_DOMAIN", default=None)
        self.ACCESS_TOKEN_COOKIE_NAME = "access_token"
        self.REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

        # Database
        self.DATABASE_URL = env.str("DATABASE_URL")

        # Application
        self.APP_NAME = "Blog Post API"
        self.APP_VERSION = "1.0.0"
        self.DEBUG = env.bool("DEBUG", default=False)
        self.ENVIRONMENT = env.str("ENVIRONMENT", default="development")

        # File Upload
        self.UPLOAD_DIR = BASE_DIR / "uploads"
        self.MAX_UPLOAD_SIZE = env.int(
            "MAX_UPLOAD_SIZE", default=2 * 1024 * 1024
        )  # 2MB
        self.ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

        # CORS Settings
        self.CORS_ORIGINS: List[str] = env.list(
            "CORS_ORIGINS",
            default=[
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
            ],
        )
        self.CORS_ALLOW_CREDENTIALS = True
        self.CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        self.CORS_ALLOW_HEADERS = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
        ]
        self.CORS_EXPOSE_HEADERS = ["X-Process-Time-ms", "X-Request-ID"]
        self.CORS_MAX_AGE = 600  # 10 minutes

        # Security
        self.PASSWORD_MIN_LENGTH = 8
        self.RATE_LIMIT_PER_MINUTE = 60

        # Admin
        self.ADMIN_USERNAME = env.str("ADMIN_USERNAME", default="admin")
        self.ADMIN_EMAIL = env.str("ADMIN_EMAIL", default="admin@example.com")
        self.ADMIN_PASSWORD = env.str("ADMIN_PASSWORD", default="AdminPassword123!")

        # Validate settings
        self._validate()

    def _validate(self):
        """Validate settings after initialization."""
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY or SECRET_KEY must be set")
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"


settings = Settings()
