"""Celery tasks for YouTube video/audio downloads.

Each task runs inside a Celery worker process (separate from the FastAPI
process).  Progress is written to Redis directly for real-time polling.
"""

from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from hashlib import sha256

import yt_dlp
from celery import Task
from celery.exceptions import Ignore

from app.celery_app import celery_app
from app.config import get_settings
from app.storage import get_storage
from app.utils.helpers import (
    find_ffmpeg,
    apply_cookies,
)

logger = logging.getLogger(__name__)

_FFMPEG_PATH = find_ffmpeg()

# ── Redis progress helpers ────────────────────────────────────

_PROGRESS_PREFIX = "ytdl:progress:"


def _redis_client():
    from redis import Redis as SyncRedis
    settings = get_settings()
    return SyncRedis.from_url(
        settings.REDIS_CELERY_URL,
        decode_responses=True,
        socket_timeout=2,
    )


def _write_progress(task_id: str, **fields):
    """Write progress fields to Redis as a JSON hash entry."""
    r = _redis_client()
    key = f"{_PROGRESS_PREFIX}{task_id}"
    try:
        # Merge with existing
        existing = r.get(key)
        if existing:
            data = json.loads(existing)
        else:
            data = {}
        data.update(fields)
        data["task_id"] = task_id
        r.setex(key, 1800, json.dumps(data))  # 30 min TTL
    except Exception as exc:
        logger.warning("Failed to write progress to Redis: %s", exc)


def _read_progress(task_id: str) -> dict | None:
    """Read progress for a task from Redis."""
    r = _redis_client()
    key = f"{_PROGRESS_PREFIX}{task_id}"
    try:
        data = r.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


def _clear_progress(task_id: str):
    r = _redis_client()
    try:
        r.delete(f"{_PROGRESS_PREFIX}{task_id}")
    except Exception:
        pass


# ── Progress hook for yt-dlp ─────────────────────────────────

def _make_progress_hook(task_id: str):
    """Return a yt-dlp progress_hook that writes to Redis."""

    def hook(d: dict):
        status = d.get("status", "")
        state = {"status": status}

        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            state["percent"] = round((downloaded / total * 100), 1) if total > 0 else 0.0
            state["speed"] = d.get("_speed_str", "") or ""
            state["eta"] = d.get("_eta_str", "") or ""
            state["filename"] = os.path.basename(d.get("filename", ""))
        elif status == "finished":
            state["percent"] = 100.0
            state["status"] = "processing"
            state["filename"] = os.path.basename(d.get("filename", ""))
        elif status == "error":
            state["error_msg"] = d.get("_error_str", "Unknown error")

        _write_progress(task_id, **state)

    return hook


# ── Format resolvers ─────────────────────────────────────────

def _resolve_video_format(quality: str) -> str:
    mapping = {
        "highest": "bestvideo+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    }
    return mapping.get(quality.lower(), "bestvideo+bestaudio/best")


def _find_output_file(download_dir: str, prefix: str) -> str:
    """Find the newest completed file in *download_dir* starting with *prefix*.

    Skips .part / .fragment / .ytdl temp files.
    """
    try:
        candidates = []
        for p in Path(download_dir).iterdir():
            name = p.name
            if not name.startswith(prefix):
                continue
            if any(name.endswith(ext) for ext in (".part", ".fragment", ".ytdl")):
                continue
            if p.is_file():
                candidates.append(p)
        if not candidates:
            return ""
        candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return str(candidates[0].resolve())
    except Exception:
        return ""


def _default_opts(task_id: str, download_dir: str) -> dict:
    """Base yt-dlp options shared by all download tasks."""
    prefix = f"yt_{task_id}_"
    outtmpl = os.path.join(download_dir, f"{prefix}%(title)s.%(ext)s")
    opts: dict = {
        "outtmpl": outtmpl,
        "progress_hooks": [_make_progress_hook(task_id)],
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }
    if _FFMPEG_PATH:
        opts["ffmpeg_location"] = _FFMPEG_PATH
    apply_cookies(opts, download=True)
    return opts


# ── Celery base task with custom on-failure ──────────────────

class YouTubeTask(Task):
    """Base class for YouTube tasks — handles progress cleanup."""

    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        _write_progress(task_id, status="error", error_msg=str(exc))
        logger.error("Task %s failed: %s", task_id, exc)


# ── Tasks ─────────────────────────────────────────────────────

@celery_app.task(
    base=YouTubeTask,
    bind=True,
    name="youtube.preview",
    acks_late=False,  # preview is idempotent, safe to retry
)
def preview_video(self, url: str) -> dict:
    """Extract video metadata (synchronous, runs in worker)."""
    try:
        opts: dict = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        if _FFMPEG_PATH:
            opts["ffmpeg_location"] = _FFMPEG_PATH
        apply_cookies(opts, download=False)

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("No video info returned")

            formats = []
            for f in (info.get("formats") or []):
                formats.append({
                    "format_id": f.get("format_id"),
                    "height": f.get("height"),
                    "ext": f.get("ext"),
                    "filesize": f.get("filesize"),
                    "vcodec": f.get("vcodec"),
                    "acodec": f.get("acodec"),
                    "tbr": f.get("tbr"),
                })

            return {
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", info.get("channel", "Unknown")),
                "thumbnail": info.get("thumbnail", ""),
                "webpage_url": info.get("webpage_url", url),
                "formats": formats[:20],
            }
    except Exception as e:
        raise RuntimeError(f"Preview failed: {e}") from e


@celery_app.task(
    base=YouTubeTask,
    bind=True,
    name="youtube.download_video",
    acks_late=True,
    max_retries=2,
    default_retry_delay=10,
)
def download_video(
    self,
    url: str,
    quality: str = "highest",
    download_dir: str = "",
) -> dict:
    """Download a YouTube video as MP4 (Celery worker task)."""
    task_id = self.request.id
    _write_progress(task_id, status="queued", percent=0.0)

    try:
        settings = get_settings()
        dl_dir = download_dir or settings.DOWNLOAD_DIR
        os.makedirs(dl_dir, exist_ok=True)

        opts = _default_opts(task_id, dl_dir)
        opts["format"] = _resolve_video_format(quality)

        _write_progress(task_id, status="downloading", percent=0.0)

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url.strip()])

        prefix = f"yt_{task_id}_"
        output_path = _find_output_file(dl_dir, prefix)
        if not output_path:
            raise RuntimeError("Output file not found after download")

        # ── Upload to storage backend ─────────────────────────
        storage = get_storage()
        remote_key = storage.store(output_path)

        download_url = None
        if isinstance(storage, __import__("app.storage", fromlist=["S3Storage"]).S3Storage):
            filename = os.path.basename(output_path)
            download_url = storage.get_download_url(remote_key, filename)
            # Remove local temp file after upload
            try:
                os.remove(output_path)
            except Exception:
                pass

        _write_progress(
            task_id,
            status="done",
            percent=100.0,
            output_path=output_path,
            download_url=download_url or "",
        )

        return {
            "status": "done",
            "output_path": output_path,
            "download_url": download_url,
        }

    except Exception as exc:
        _write_progress(task_id, status="error", error_msg=str(exc))
        raise Ignore() from exc


@celery_app.task(
    base=YouTubeTask,
    bind=True,
    name="youtube.download_audio",
    acks_late=True,
    max_retries=2,
    default_retry_delay=10,
)
def download_audio(
    self,
    url: str,
    quality: str = "192",
    download_dir: str = "",
) -> dict:
    """Download YouTube audio as MP3 (Celery worker task)."""
    task_id = self.request.id
    _write_progress(task_id, status="queued", percent=0.0)

    try:
        settings = get_settings()
        dl_dir = download_dir or settings.DOWNLOAD_DIR
        os.makedirs(dl_dir, exist_ok=True)

        opts = _default_opts(task_id, dl_dir)
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ]

        _write_progress(task_id, status="downloading", percent=0.0)

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url.strip()])

        prefix = f"yt_{task_id}_"
        output_path = _find_output_file(dl_dir, prefix)
        if not output_path:
            # Could be .mp3 extension instead of .mp4
            candidates = list(Path(dl_dir).glob(f"{prefix}*"))
            if candidates:
                candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                output_path = str(candidates[0].resolve())
        if not output_path:
            raise RuntimeError("Output file not found after download")

        # ── Upload to storage backend ─────────────────────────
        storage = get_storage()
        remote_key = storage.store(output_path)

        download_url = None
        from app.storage import S3Storage
        if isinstance(storage, S3Storage):
            filename = os.path.basename(output_path)
            download_url = storage.get_download_url(remote_key, filename)
            try:
                os.remove(output_path)
            except Exception:
                pass

        _write_progress(
            task_id,
            status="done",
            percent=100.0,
            output_path=output_path,
            download_url=download_url or "",
        )

        return {
            "status": "done",
            "output_path": output_path,
            "download_url": download_url,
        }

    except Exception as exc:
        _write_progress(task_id, status="error", error_msg=str(exc))
        raise Ignore() from exc
