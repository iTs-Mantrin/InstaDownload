"""YouTube API routes."""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse

from app.schemas import (
    DownloadRequest,
    DownloadResponse,
    ProgressResponse,
    YouTubePreview,
    ErrorResponse,
)
from app.services.youtube_service import YouTubeService
from app.utils.helpers import (
    is_youtube_url,
    is_valid_url,
    generate_task_id,
    clean_old_files,
)
from app.config import get_settings

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])
settings = get_settings()


@router.post("/preview", response_model=YouTubePreview)
def preview_youtube(url: str = Body(..., embed=True)):
    """Get video metadata before downloading."""
    if not is_valid_url(url) or not is_youtube_url(url):
        raise HTTPException(400, "Invalid YouTube URL")
    info = YouTubeService.extract_info(url)
    if not info:
        raise HTTPException(400, "Could not fetch video info")
    return info


@router.post("/download", response_model=DownloadResponse)
def download_youtube(req: DownloadRequest):
    """Start a YouTube download task."""
    if not is_valid_url(req.url) or not is_youtube_url(req.url):
        raise HTTPException(400, "Invalid YouTube URL")

    os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
    clean_old_files(settings.DOWNLOAD_DIR, settings.MAX_FILE_AGE_MINUTES)

    task_id = generate_task_id()
    YouTubeService.start_download(
        task_id=task_id,
        url=req.url,
        quality=req.quality or "highest",
        audio_only=req.audio_only,
        download_dir=settings.DOWNLOAD_DIR,
    )
    return DownloadResponse(task_id=task_id, source="youtube", status="queued")


@router.get("/progress/{task_id}", response_model=ProgressResponse)
def get_youtube_progress(task_id: str):
    """Poll YouTube download progress."""
    state = YouTubeService.get_progress(task_id)
    if state is None:
        raise HTTPException(404, "Task not found")

    # If the task provided a download_url (e.g. S3 presigned URL), use it.
    # Otherwise fall back to the local file endpoint.
    download_url = state.get("download_url") or None
    if not download_url and state["status"] == "done" and state["output_path"]:
        download_url = f"/api/youtube/file/{task_id}"

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
def get_youtube_file(task_id: str):
    """Stream the completed YouTube file."""
    state = YouTubeService.get_progress(task_id)
    if state is None:
        raise HTTPException(404, "Task not found")
    if state["status"] != "done":
        raise HTTPException(400, "Download not yet complete")
    if not state["output_path"] or not os.path.isfile(state["output_path"]):
        raise HTTPException(404, "File not found")

    filename = os.path.basename(state["output_path"])
    YouTubeService.remove_task(task_id)
    return FileResponse(
        path=state["output_path"],
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{task_id}")
def cancel_youtube(task_id: str):
    """Cancel a running YouTube download."""
    state = YouTubeService.get_progress(task_id)
    if state is None:
        raise HTTPException(404, "Task not found")
    YouTubeService.cancel(task_id)
    return {"status": "cancelled"}
