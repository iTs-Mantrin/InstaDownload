import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "YouTube Downloader API"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: Any = ["*"]
    temp_dir: Path = Path("/tmp/youtube-downloader")
    download_token_secret: str = "change-me-in-production"
    download_token_ttl_seconds: int = 900
    yt_dlp_cookies_file: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            if not value.strip():
                return ["*"]
            # Try JSON first (supports ["*"] or ["http://..."])
            try:
                parsed = json.loads(value.strip())
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
            # Fallback: comma-separated (http://a.com,http://b.com)
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["*"]

    @field_validator("temp_dir", mode="before")
    @classmethod
    def parse_temp_dir(cls, value: str | Path) -> Path:
        return Path(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
