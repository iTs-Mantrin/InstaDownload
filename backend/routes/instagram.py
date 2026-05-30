import threading
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.background import BackgroundTask
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from utils.download_manager import DownloadTask, TaskCancelledError, manager
from utils.temp_files import find_downloaded_file
from utils.config import get_settings

router = APIRouter(prefix="/instagram", tags=["instagram"])


# ── POST /api/instagram/preview ─────────────────────────

@router.post("/preview")
async def preview_instagram(payload: dict):
    url = _validate_url(payload)
    raw = _extract_raw_info(url)

    formats = _build_format_list(raw.get("formats", []))

    return {
        "title": raw.get("title") or "Instagram Media",
        "duration": int(raw.get("duration") or 0),
        "uploader": raw.get("channel") or raw.get("uploader") or "Unknown",
        "webpage_url": raw.get("webpage_url") or url,
        "thumbnail": raw.get("thumbnail") or "",
        "formats": formats,
    }


# ── POST /api/instagram/download ────────────────────────

@router.post("/download")
async def download_instagram(payload: dict, request: Request):
    url = _validate_url(payload)

    task = manager.create_task()
    task.status = "running"

    base_url = str(request.base_url).rstrip("/")

    thread = threading.Thread(
        target=_run_download,
        args=(task, url, base_url),
        daemon=True,
    )
    thread.start()

    return {"task_id": task.task_id, "source": "instagram"}


# ── GET /api/instagram/progress/{task_id} ────────────────

@router.get("/progress/{task_id}")
async def get_download_progress(task_id: str, request: Request):
    task = manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict(base_url=str(request.base_url).rstrip("/"))


# ── GET /api/instagram/file/{task_id} ──────────────────

@router.get("/file/{task_id}")
async def get_downloaded_file(task_id: str):
    task = manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "done" or task.file_path is None:
        raise HTTPException(status_code=400, detail="Download not ready yet")
    if not task.file_path.exists():
        raise HTTPException(status_code=404, detail="File no longer available")

    media_type = _guess_media_type(task.file_path.name)

    def _cleanup() -> None:
        manager.remove_task(task_id)

    return FileResponse(
        path=task.file_path,
        filename=task.file_path.name,
        media_type=media_type,
        background=BackgroundTask(_cleanup),
    )


# ── DELETE /api/instagram/{task_id} ─────────────────────

@router.delete("/{task_id}")
async def cancel_download(task_id: str):
    task = manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.cancel()
    return {"status": "cancelled"}


# ── POST /api/instagram/stories ─────────────────────────

@router.post("/stories")
async def download_stories(username: str, request: Request):
    if not username or not username.strip():
        raise HTTPException(status_code=400, detail="username is required")

    task = manager.create_task()
    task.status = "running"

    base_url = str(request.base_url).rstrip("/")

    thread = threading.Thread(
        target=_run_stories_download,
        args=(task, username.strip(), base_url),
        daemon=True,
    )
    thread.start()

    return {"task_id": task.task_id, "source": "instagram"}


# ── GET /api/instagram/profile-pic/{username} ───────────

@router.get("/profile-pic/{username}")
async def get_profile_pic(username: str):
    url = f"https://www.instagram.com/{username}/"
    settings = get_settings()
    opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "noplaylist": True,
        "cookiefile": settings.yt_dlp_cookies_file,
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if isinstance(info, dict):
                thumb_url = (
                    info.get("thumbnail")
                    or (info.get("thumbnails") or [{}])[0].get("url")
                )
                if thumb_url:
                    return RedirectResponse(url=thumb_url)
    except DownloadError:
        pass
    raise HTTPException(status_code=404, detail="Profile not found or profile picture unavailable")


# ── Internal helpers ──────────────────────────────────────


def _validate_url(payload: dict) -> str:
    url = payload.get("url", "")
    if not url or not isinstance(url, str) or not url.strip():
        raise HTTPException(status_code=400, detail="url is required")
    return url.strip()


def _extract_raw_info(url: str) -> dict:
    settings = get_settings()
    opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "noplaylist": True,
        "cookiefile": settings.yt_dlp_cookies_file,
    }
    try:
        with YoutubeDL(opts) as ydl:
            result = ydl.extract_info(url, download=False)
            return result if isinstance(result, dict) else {}
    except DownloadError as e:
        msg = str(e).strip() or "Failed to fetch media info"
        lowered = msg.lower()
        if "private" in lowered or "not available" in lowered:
            raise HTTPException(status_code=404, detail="This content is unavailable or private.")
        if "login" in lowered or "sign in" in lowered or "auth" in lowered:
            raise HTTPException(status_code=403, detail="This content requires authentication.")
        raise HTTPException(status_code=400, detail=msg)


def _build_format_list(raw_formats: list) -> list[dict]:
    result = []
    for fmt in raw_formats:
        if not isinstance(fmt, dict):
            continue
        result.append(
            {
                "format_id": fmt.get("format_id", ""),
                "height": fmt.get("height"),
                "ext": fmt.get("ext", ""),
                "filesize": fmt.get("filesize") or fmt.get("filesize_approx"),
                "vcodec": fmt.get("vcodec", ""),
                "acodec": fmt.get("acodec", ""),
                "tbr": fmt.get("tbr") or fmt.get("average_bitrate"),
            }
        )
    return result


def _run_download(task: DownloadTask, url: str, base_url: str) -> None:
    settings = get_settings()
    try:
        output_template = str(task.directory / "%(title).120B-%(id)s.%(ext)s")
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "outtmpl": output_template,
            "progress_hooks": [_make_progress_hook(task)],
            "cookiefile": settings.yt_dlp_cookies_file,
        }

        with YoutubeDL(options) as ydl:
            ydl.download([url])

        # Instagram may produce .mp4 (video) or .jpg (image)
        file_path = _find_any_file(task.directory)
        if file_path is None:
            task.status = "error"
            task.error_msg = "Download completed but output file not found"
            return

        task.file_path = file_path
        task.filename = file_path.name
        task.progress = 100.0
        task.status = "done"
        task.download_url = f"{base_url}/api/instagram/file/{task.task_id}"

    except TaskCancelledError:
        task.status = "cancelled"
    except DownloadError as e:
        task.status = "error"
        task.error_msg = str(e).strip() or "Download failed"
    except Exception as e:
        task.status = "error"
        task.error_msg = (str(e)[:500]) if str(e) else "Unknown error"


def _run_stories_download(task: DownloadTask, username: str, base_url: str) -> None:
    settings = get_settings()
    try:
        url = f"https://www.instagram.com/stories/{username}/"
        output_template = str(task.directory / "%(title).120B-%(id)s.%(ext)s")
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "outtmpl": output_template,
            "progress_hooks": [_make_progress_hook(task)],
            "cookiefile": settings.yt_dlp_cookies_file,
        }

        with YoutubeDL(options) as ydl:
            ydl.download([url])

        # Collect all downloaded files
        files = _list_files(task.directory)
        if not files:
            task.status = "error"
            task.error_msg = "No stories found or account has no active stories"
            return

        if len(files) == 1:
            # Single file — serve directly
            f = files[0]
            task.file_path = f
            task.filename = f.name
        else:
            # Multiple files — ZIP them together
            zip_path = task.directory / f"{username}_stories.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in files:
                    zf.write(f, f.name)
            task.file_path = zip_path
            task.filename = zip_path.name

        task.progress = 100.0
        task.status = "done"
        task.download_url = f"{base_url}/api/instagram/file/{task.task_id}"

    except TaskCancelledError:
        task.status = "cancelled"
    except DownloadError as e:
        msg = str(e).strip() or "Download failed"
        lowered = msg.lower()
        if "login" in lowered or "sign in" in lowered or "auth" in lowered:
            task.error_msg = "Stories require authentication. Set up Instagram cookies in the backend."
        else:
            task.error_msg = msg
        task.status = "error"
    except Exception as e:
        task.status = "error"
        task.error_msg = (str(e)[:500]) if str(e) else "Unknown error"


def _find_any_file(directory: Path) -> Path | None:
    """Find the most recently created file in a directory (any extension)."""
    return find_downloaded_file(directory, "")


def _list_files(directory: Path) -> list[Path]:
    """Return all regular files in a directory sorted by modification time (newest first)."""
    return sorted(
        (p for p in directory.iterdir() if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def _make_progress_hook(task: DownloadTask):
    def hook(d: dict) -> None:
        if task.is_cancelled:
            raise TaskCancelledError()
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            task.progress = min((downloaded / total * 100) if total > 0 else 0, 99.9)
            task.speed = d.get("_speed_str", "") or ""
            task.eta = d.get("_eta_str", "") or ""
            raw_filename = d.get("filename", "")
            task.filename = Path(raw_filename).name if raw_filename else ""
        elif status == "finished":
            task.progress = 100.0
            raw_filename = d.get("filename", "")
            task.filename = Path(raw_filename).name if raw_filename else ""

    return hook


def _guess_media_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return {
        ".mp4": "video/mp4",
        ".mp3": "audio/mpeg",
        ".webm": "video/webm",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".zip": "application/zip",
    }.get(ext, "application/octet-stream")
