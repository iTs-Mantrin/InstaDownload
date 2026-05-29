"""Pydantic schemas for API request/response."""

from pydantic import BaseModel, Field
from typing import Optional


class DownloadRequest(BaseModel):
    url: str = Field(..., min_length=1, description="Media URL to download")
    source: str = Field(
        default="", description="youtube / instagram / auto-detect if empty"
    )
    quality: str = Field(default="highest", description="Quality for YouTube")
    audio_only: bool = Field(default=False, description="MP3 only (YouTube)")
    username: Optional[str] = Field(
        default=None, description="Instagram username for stories/profile pic"
    )


class DownloadResponse(BaseModel):
    task_id: str
    source: str
    status: str = "queued"
    message: str = "Download started"


class ProgressResponse(BaseModel):
    task_id: str
    percent: float = 0.0
    speed: str = ""
    eta: str = ""
    filename: str = ""
    status: str = "queued"
    error_msg: str = ""
    download_url: Optional[str] = None


class YouTubePreview(BaseModel):
    title: str
    duration: int
    uploader: str
    thumbnail: str
    webpage_url: str
    formats: list[dict] = []


class InstagramPreview(BaseModel):
    title: str
    type: str  # post / reel / carousel
    thumbnail: str
    username: str
    description: str = ""


class ErrorResponse(BaseModel):
    detail: str
    code: str = "error"
