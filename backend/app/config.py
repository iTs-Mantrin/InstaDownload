"""Application configuration from environment variables."""

import os
from functools import lru_cache


class Settings:
    # App
    APP_NAME: str = "InstaDownload"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")

    # Server
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))
    # Use "*" for development. In production, set to specific origins like "https://frontend.railway.app"
    CORS_ORIGINS: list[str] = os.environ.get("CORS_ORIGINS", "*").split(",")

    # Database (PostgreSQL)
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/instadownload",
    )

    # Redis
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Downloads
    DOWNLOAD_DIR: str = os.environ.get("DOWNLOAD_DIR", "/tmp/instadownload")
    MAX_FILE_AGE_MINUTES: int = int(os.environ.get("MAX_FILE_AGE_MINUTES", "30"))
    MAX_CONCURRENT_DOWNLOADS: int = int(
        os.environ.get("MAX_CONCURRENT_DOWNLOADS", "10")
    )

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30"))

    # yt-dlp
    YT_DLP_COOKIES_FILE: str | None = os.environ.get("YT_DLP_COOKIES_FILE")
    YT_DLP_USER_AGENT: str | None = os.environ.get(
        "YT_DLP_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
