"""Application configuration from environment variables."""

import os
from functools import lru_cache
from pathlib import Path


def _load_dotenv():
    """Load .env from the backend directory (local dev only)."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.is_file():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip()
                # Strip surrounding quotes
                if len(val) > 1 and val[0] == val[-1] and val[0] in ('"', "'"):
                    val = val[1:-1]
                if key not in os.environ:  # don't override already-set env
                    os.environ[key] = val


_load_dotenv()


class Settings:
    # App
    APP_NAME: str = "InstaDownload"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")

    # Server
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))
    CORS_ORIGINS: list[str] = os.environ.get("CORS_ORIGINS", "*").split(",")

    # Redis (optional — used for cache, no crash if missing)
    REDIS_URL: str = os.environ.get("REDIS_URL", "")

    # Downloads
    DOWNLOAD_DIR: str = os.environ.get("DOWNLOAD_DIR", "/tmp/instadownload")
    MAX_FILE_AGE_MINUTES: int = int(os.environ.get("MAX_FILE_AGE_MINUTES", "30"))
    MAX_CONCURRENT_DOWNLOADS: int = int(
        os.environ.get("MAX_CONCURRENT_DOWNLOADS", "10")
    )

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30"))

    # PostgreSQL / Supabase
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "",
    )
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.environ.get(
        "SUPABASE_PUBLISHABLE_KEY", ""
    )

    @property
    def db_configured(self) -> bool:
        """True if DATABASE_URL is set and not a placeholder."""
        url = self.DATABASE_URL
        if not url:
            return False
        # Ignore placeholder values
        if "YOUR-PASSWORD" in url or "YOUR_SUPABASE_DB_PASSWORD" in url:
            return False
        return True

    # yt-dlp
    YT_DLP_COOKIES_FILE: str | None = os.environ.get("YT_DLP_COOKIES_FILE")
    YT_DLP_USER_AGENT: str | None = os.environ.get(
        "YT_DLP_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
