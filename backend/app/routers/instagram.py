"""Instagram API routes."""

import os
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import FileResponse

from app.schemas import (
    DownloadRequest,
    DownloadResponse,
    ProgressResponse,
    InstagramPreview,
)
from app.services.instagram_service import InstagramService
from app.utils.helpers import (
    is_instagram_url,
    is_valid_url,
    generate_task_id,
    clean_old_files,
)
from app.config import get_settings

router = APIRouter(prefix="/api/instagram", tags=["Instagram"])
settings = get_settings()


@router.post("/preview", response_model=InstagramPreview)
def preview_instagram(url: str = Body(..., embed=True)):
    """Preview Instagram media metadata."""
    if not is_valid_url(url) or not is_instagram_url(url):
        raise HTTPException(400, "Invalid Instagram URL")
    info = InstagramService.extract_info(url)
    if not info:
        raise HTTPException(400, "Could not fetch media info")
    return info


@router.post("/download", response_model=DownloadResponse)
def download_instagram(req: DownloadRequest):
    """Download an Instagram post/reel by URL."""
    if not is_valid_url(req.url) or not is_instagram_url(req.url):
        raise HTTPException(400, "Invalid Instagram URL")

    os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
    clean_old_files(settings.DOWNLOAD_DIR, settings.MAX_FILE_AGE_MINUTES)

    task_id = generate_task_id()
    InstagramService.start_download(
        task_id=task_id, url=req.url, download_dir=settings.DOWNLOAD_DIR
    )
    return DownloadResponse(task_id=task_id, source="instagram", status="queued")


@router.post("/stories", response_model=DownloadResponse)
def download_stories(username: str = Query(..., min_length=1)):
    """Download Instagram stories for a username (requires cookies)."""
    os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
    task_id = generate_task_id()
    InstagramService.start_story_download(
        task_id=task_id, username=username, download_dir=settings.DOWNLOAD_DIR
    )
    return DownloadResponse(
        task_id=task_id, source="instagram", status="queued", message="Stories download attempted"
    )


@router.get("/profile-pic/{username}")
def get_profile_pic(username: str):
    """Download Instagram profile picture."""
    os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
    path = InstagramService.download_profile_pic(username, settings.DOWNLOAD_DIR)
    if not path or not os.path.isfile(path):
        raise HTTPException(404, "Could not download profile picture")
    filename = os.path.basename(path)
    return FileResponse(
        path=path,
        filename=filename,
        media_type="image/jpeg",
    )


@router.get("/progress/{task_id}", response_model=ProgressResponse)
def get_ig_progress(task_id: str):
    """Poll Instagram download progress."""
    state = InstagramService.get_progress(task_id)
    if state is None:
        raise HTTPException(404, "Task not found")

    download_url = None
    if state["status"] == "done" and state["output_path"]:
        download_url = f"/api/instagram/file/{task_id}"

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
def get_ig_file(task_id: str):
    """Stream the completed Instagram file."""
    state = InstagramService.get_progress(task_id)
    if state is None:
        raise HTTPException(404, "Task not found")
    if state["status"] != "done":
        raise HTTPException(400, "Download not yet complete")
    if not state["output_path"] or not os.path.isfile(state["output_path"]):
        raise HTTPException(404, "File not found")

    filename = os.path.basename(state["output_path"])
    InstagramService.remove_task(task_id)
    return FileResponse(
        path=state["output_path"],
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{task_id}")
def cancel_ig(task_id: str):
    """Cancel a running Instagram download."""
    state = InstagramService.get_progress(task_id)
    if state is None:
        raise HTTPException(404, "Task not found")
    InstagramService.cancel(task_id)
    return {"status": "cancelled"}
