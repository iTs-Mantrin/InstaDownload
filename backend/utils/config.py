from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "YouTube Downloader API"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    temp_dir: Path = Path("/tmp/youtube-downloader")
    download_token_secret: str = "change-me-in-production"
    download_token_ttl_seconds: int = 900
    yt_dlp_cookies_file: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]

    @field_validator("temp_dir", mode="before")
    @classmethod
    def parse_temp_dir(cls, value: str | Path) -> Path:
        return Path(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
