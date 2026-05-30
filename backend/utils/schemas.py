from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class VideoInfoRequest(BaseModel):
    url: str = Field(..., min_length=1)


class FormatOption(BaseModel):
    format: Literal["mp4", "mp3"]
    quality: str
    label: str
    extension: str
    filesize: int | None = None


class VideoInfoResponse(BaseModel):
    title: str
    thumbnail: str | None = None
    duration: int
    formats: list[FormatOption]


class DownloadRequest(BaseModel):
    url: str = Field(..., min_length=1)
    format: Literal["mp4", "mp3"]
    quality: str = Field(..., min_length=1)


class DownloadResponse(BaseModel):
    download_url: str
    filename: str
    format: Literal["mp4", "mp3"]
    quality: str
    expires_in: int
    extension: str


class ErrorResponse(BaseModel):
    detail: str


class DownloadedFile(BaseModel):
    file_path: Path
    filename: str
    media_type: str
    directory: Path

    model_config = {"arbitrary_types_allowed": True}
