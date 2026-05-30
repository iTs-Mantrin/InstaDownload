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


# ── Frontend-compatible schemas (match TypeScript interfaces in client.ts) ──


class FrontendFormatInfo(BaseModel):
    format_id: str
    height: int | None = None
    ext: str = ""
    filesize: int | None = None
    vcodec: str = ""
    acodec: str = ""
    tbr: float | None = None


class FrontendPreviewResponse(BaseModel):
    title: str
    duration: int = 0
    uploader: str = "Unknown"
    webpage_url: str = ""
    thumbnail: str = ""
    formats: list[FrontendFormatInfo] = []


class FrontendProgressResponse(BaseModel):
    percent: float = 0.0
    speed: str = ""
    eta: str = ""
    filename: str = ""
    status: str = "queued"
    error_msg: str = ""
    download_url: str | None = None


class FrontendDownloadResponse(BaseModel):
    task_id: str
    source: str = "youtube"
