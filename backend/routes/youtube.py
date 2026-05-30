import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from utils.download_manager import DownloadTask, TaskCancelledError, manager
from utils.temp_files import find_downloaded_file
from utils.config import get_settings

router = APIRouter(prefix="/youtube", tags=["youtube-frontend"])


# ── POST /api/youtube/preview ─────────────────────────────

@router.post("/preview")
async def preview_youtube(payload: dict):
    url = _validate_url(payload)
    raw = _extract_raw_info(url)

    formats = _build_format_list(raw.get("formats", []))

    return {
        "title": raw.get("title") or "Unknown title",
        "duration": int(raw.get("duration") or 0),
        "uploader": raw.get("channel") or raw.get("uploader") or "Unknown",
        "webpage_url": raw.get("webpage_url") or url,
        "thumbnail": raw.get("thumbnail") or "",
        "formats": formats,
    }


# ── POST /api/youtube/download ────────────────────────────

@router.post("/download")
async def download_youtube(payload: dict, request: Request):
    url = _validate_url(payload)
    quality = payload.get("quality", "highest")
    audio_only = bool(payload.get("audio_only", False))

    task = manager.create_task()
    task.status = "running"

    base_url = str(request.base_url).rstrip("/")

    thread = threading.Thread(
        target=_run_download,
        args=(task, url, quality, audio_only, base_url),
        daemon=True,
    )
    thread.start()

    return {"task_id": task.task_id, "source": "youtube"}


# ── GET /api/youtube/progress/{task_id} ───────────────────

@router.get("/progress/{task_id}")
async def get_download_progress(task_id: str, request: Request):
    task = manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict(base_url=str(request.base_url).rstrip("/"))


# ── GET /api/youtube/file/{task_id} ─────────────────────

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
    directory = task.directory

    def _cleanup() -> None:
        manager.remove_task(task_id)

    return FileResponse(
        path=task.file_path,
        filename=task.file_path.name,
        media_type=media_type,
        background=BackgroundTask(_cleanup),
    )


# ── DELETE /api/youtube/{task_id} ─────────────────────────

@router.delete("/{task_id}")
async def cancel_download(task_id: str):
    task = manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.cancel()
    return {"status": "cancelled"}


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
        "extractor_retries": 2,
        "socket_timeout": 30,
        "cookiefile": settings.yt_dlp_cookies_file,
    }
    try:
        with YoutubeDL(opts) as ydl:
            result = ydl.extract_info(url, download=False)
            return result if isinstance(result, dict) else {}
    except DownloadError as e:
        msg = str(e).strip() or "Failed to fetch video info"
        lowered = msg.lower()
        if "private video" in lowered or "video is private" in lowered:
            raise HTTPException(status_code=403, detail="This video is private and cannot be accessed.")
        if "sign in to confirm your age" in lowered or "age-restricted" in lowered:
            raise HTTPException(status_code=403, detail="This video is age-restricted.")
        if "video unavailable" in lowered or "not available" in lowered:
            raise HTTPException(status_code=404, detail="The requested video is unavailable.")
        if "sign in to confirm" in lowered and "bot" in lowered:
            raise HTTPException(
                status_code=403,
                detail="YouTube requires authentication. The server needs cookies set up. "
                       "Set YT_DLP_COOKIES_FILE environment variable with a valid cookies.txt file.",
            )
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


def _run_download(task: DownloadTask, url: str, quality: str, audio_only: bool, base_url: str) -> None:
    settings = get_settings()
    try:
        output_template = str(task.directory / "%(title).120B-%(id)s.%(ext)s")
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "outtmpl": output_template,
            "progress_hooks": [_make_progress_hook(task)],
            "extractor_retries": 2,
            "socket_timeout": 30,
            "cookiefile": settings.yt_dlp_cookies_file,
        }

        if audio_only:
            q = quality if quality in ("128", "192", "320") else "192"
            options.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": q,
                        }
                    ],
                    "final_ext": "mp3",
                }
            )
            expected_ext = ".mp3"
        else:
            fmt_selector = _build_video_format_selector(quality)
            options.update(
                {
                    "format": fmt_selector,
                    "merge_output_format": "mp4",
                    "final_ext": "mp4",
                }
            )
            expected_ext = ".mp4"

        with YoutubeDL(options) as ydl:
            ydl.download([url])

        file_path = find_downloaded_file(task.directory, expected_ext)
        if file_path is None:
            task.status = "error"
            task.error_msg = "Download completed but output file not found"
            return

        task.file_path = file_path
        task.filename = file_path.name
        task.progress = 100.0
        task.status = "done"
        task.download_url = f"{base_url}/api/youtube/file/{task.task_id}"

    except TaskCancelledError:
        task.status = "cancelled"
    except DownloadError as e:
        msg = str(e).strip() or "Download failed"
        lowered = msg.lower()
        if "sign in to confirm" in lowered and "bot" in lowered:
            msg = (
                "YouTube requires authentication. "
                "The server owner must set YT_DLP_COOKIES_FILE with a valid cookies.txt file. "
                "See: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"
            )
        task.status = "error"
        task.error_msg = msg
    except Exception as e:
        task.status = "error"
        task.error_msg = (str(e)[:500]) if str(e) else "Unknown error"


def _build_video_format_selector(quality: str) -> str:
    q = quality.lower().replace("p", "").strip()
    if q == "highest" or not q.isdigit():
        return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    return f"bestvideo[ext=mp4][height<={q}]+bestaudio[ext=m4a]/best[ext=mp4][height<={q}]/best[height<={q}]"


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
        ".mkv": "video/x-matroska",
    }.get(ext, "application/octet-stream")
