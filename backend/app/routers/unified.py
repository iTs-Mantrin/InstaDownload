"""Unified API router — auto-detects source (youtube/instagram) for common operations."""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse

from app.schemas import (
    DownloadRequest,
    DownloadResponse,
    ProgressResponse,
    YouTubePreview,
    InstagramPreview,
)
from app.services.youtube_service import YouTubeService
from app.services.instagram_service import InstagramService
from app.utils.helpers import (
    is_youtube_url,
    is_instagram_url,
    is_valid_url,
    generate_task_id,
    clean_old_files,
)
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["Unified"])
settings = get_settings()


def _detect_source(url: str) -> str | None:
    if is_youtube_url(url):
        return "youtube"
    if is_instagram_url(url):
        return "instagram"
    return None


def _service_for(source: str):
    if source == "youtube":
        return YouTubeService
    elif source == "instagram":
        return InstagramService
    return None


@router.post("/download", response_model=DownloadResponse)
def unified_download(req: DownloadRequest):
    """Start a download — auto-detects source if not specified."""
    if not is_valid_url(req.url):
        raise HTTPException(400, "Invalid URL")

    source = req.source or _detect_source(req.url)
    if not source:
        raise HTTPException(400, "Could not detect source — specify youtube or instagram")

    os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
    clean_old_files(settings.DOWNLOAD_DIR, settings.MAX_FILE_AGE_MINUTES)

    task_id = generate_task_id()
    svc = _service_for(source)
    if not svc:
        raise HTTPException(400, f"Unknown source: {source}")

    if source == "youtube":
        if not is_youtube_url(req.url):
            raise HTTPException(400, "Invalid YouTube URL")
        YouTubeService.start_download(
            task_id=task_id,
            url=req.url,
            quality=req.quality or "highest",
            audio_only=req.audio_only or False,
            download_dir=settings.DOWNLOAD_DIR,
        )
    else:
        if not is_instagram_url(req.url):
            raise HTTPException(400, "Invalid Instagram URL")
        InstagramService.start_download(
            task_id=task_id, url=req.url, download_dir=settings.DOWNLOAD_DIR
        )

    return DownloadResponse(task_id=task_id, source=source, status="queued")


@router.get("/progress/{task_id}", response_model=ProgressResponse)
def unified_progress(task_id: str):
    """Poll download progress — checks YouTube then Instagram."""
    state = YouTubeService.get_progress(task_id)
    source = "youtube"
    if state is None:
        state = InstagramService.get_progress(task_id)
        source = "instagram"

    if state is None:
        raise HTTPException(404, "Task not found")

    download_url = None
    if state["status"] == "done" and state.get("output_path"):
        download_url = f"/api/file/{task_id}"

    return ProgressResponse(
        task_id=task_id,
        percent=state["percent"],
        speed=state["speed"],
        eta=state["eta"],
        filename=state["filename"],
        status=state["status"],
        error_msg=state["error_msg"],
        download_url=download_url,
    )


@router.get("/file/{task_id}")
def unified_file(task_id: str):
    """Stream completed file — checks YouTube then Instagram."""
    state = YouTubeService.get_progress(task_id)
    svc = YouTubeService
    if state is None:
        state = InstagramService.get_progress(task_id)
        svc = InstagramService

    if state is None:
        raise HTTPException(404, "Task not found")
    if state["status"] != "done":
        raise HTTPException(400, "Download not yet complete")
    if not state.get("output_path") or not os.path.isfile(state["output_path"]):
        raise HTTPException(404, "File not found")

    filename = os.path.basename(state["output_path"])
    svc.remove_task(task_id)
    return FileResponse(
        path=state["output_path"],
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/cancel/{task_id}")
def unified_cancel(task_id: str):
    """Cancel a running download."""
    state = YouTubeService.get_progress(task_id)
    svc = YouTubeService
    if state is None:
        state = InstagramService.get_progress(task_id)
        svc = InstagramService

    if state is None:
        raise HTTPException(404, "Task not found")
    svc.cancel(task_id)
    return {"status": "cancelled"}


class PreviewRequest(BaseModel):
    url: str
    source: str = ""


@router.post("/preview")
def unified_preview(req: PreviewRequest):
    """Preview media metadata — auto-detects source."""
    if not is_valid_url(req.url):
        raise HTTPException(400, "Invalid URL")

    src = req.source or _detect_source(req.url)
    if not src:
        raise HTTPException(400, "Could not detect source")

    if src == "youtube":
        if not is_youtube_url(req.url):
            raise HTTPException(400, "Invalid YouTube URL")
        info = YouTubeService.extract_info(req.url)
        if not info:
            raise HTTPException(400, "Could not fetch video info")
        return info
    elif src == "instagram":
        if not is_instagram_url(req.url):
            raise HTTPException(400, "Invalid Instagram URL")
        info = InstagramService.extract_info(req.url)
        if not info:
            raise HTTPException(400, "Could not fetch media info")
        return info

    raise HTTPException(400, f"Unknown source: {src}")
