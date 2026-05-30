"""YouTube download service — submits Celery tasks.

Previously used in-process threads. Now delegates to Celery workers
for proper queue management, retries, and S3 upload support.
"""

from __future__ import annotations

import os
import json
import logging
from typing import Any

from app.config import get_settings
from app.celery_app import celery_app
from app.utils.helpers import clean_old_files

logger = logging.getLogger(__name__)

# ── Redis progress helpers (used by router to poll) ──────────

_PROGRESS_PREFIX = "ytdl:progress:"


def _redis_client():
    from redis import Redis as SyncRedis
    settings = get_settings()
    url = settings.REDIS_CELERY_URL
    if not url:
        return None
    try:
        return SyncRedis.from_url(url, decode_responses=True, socket_timeout=2)
    except Exception:
        return None


def get_celery_progress(task_id: str) -> dict[str, Any] | None:
    """Read progress written by a Celery task from Redis."""
    r = _redis_client()
    if r is None:
        return None
    key = f"{_PROGRESS_PREFIX}{task_id}"
    try:
        data = r.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


def clear_celery_progress(task_id: str):
    r = _redis_client()
    if r is None:
        return
    try:
        r.delete(f"{_PROGRESS_PREFIX}{task_id}")
    except Exception:
        pass


# ── In-memory fallback (when Redis is unreachable) ────────────

import threading

_tasks: dict[str, dict] = {}
_tasks_lock = threading.Lock()


def _fallback_get(task_id: str) -> dict | None:
    with _tasks_lock:
        return _tasks.get(task_id)


def _fallback_set(task_id: str, state: dict):
    with _tasks_lock:
        _tasks[task_id] = state


def _fallback_remove(task_id: str):
    with _tasks_lock:
        _tasks.pop(task_id, None)


# ── Service ──────────────────────────────────────────────────

class YouTubeService:
    """Handles YouTube video/audio downloads via Celery tasks."""

    @staticmethod
    def extract_info(url: str) -> dict | None:
        """Get video metadata — calls Celery task synchronously (waits for result).

        Falls back to the old in-process yt-dlp extraction if Celery call fails.
        """
        import yt_dlp
        from app.utils.helpers import apply_cookies, find_ffmpeg

        ffmpeg_path = find_ffmpeg()

        try:
            # Try Celery first (runs in worker, doesn't block the web process)
            result = celery_app.send_task(
                "youtube.preview",
                args=[url],
                queue="default",
            )
            try:
                return result.get(timeout=30, propagate=True)
            except Exception:
                logger.warning("Celery preview timeout, falling back to in-process")
        except Exception:
            logger.warning("Celery unavailable, extracting preview in-process")

        # Fallback: in-process extraction
        try:
            # Check Redis cache first
            from app.redis_cache import get_cached_preview
            import asyncio
            try:
                cached = asyncio.run(get_cached_preview(url))
                if cached:
                    return cached
            except Exception:
                pass

            opts: dict = {"quiet": True, "no_warnings": True, "extract_flat": False}
            if ffmpeg_path:
                opts["ffmpeg_location"] = ffmpeg_path
            apply_cookies(opts, download=False)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
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
                    result = {
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", info.get("channel", "Unknown")),
                        "thumbnail": info.get("thumbnail", ""),
                        "webpage_url": info.get("webpage_url", url),
                        "formats": formats[:20],
                    }
                    # Cache
                    try:
                        asyncio.run(
                            __import__("app.redis_cache", fromlist=["set_cached_preview"]).set_cached_preview(url, result)
                        )
                    except Exception:
                        pass
                    return result
        except Exception as exc:
            logger.error("In-process preview failed: %s", exc)
            # Log the actual error for debugging
            import traceback
            logger.error("Traceback:\n%s", traceback.format_exc())
        return None

    @staticmethod
    def start_download(
        task_id: str,
        url: str,
        quality: str = "highest",
        audio_only: bool = False,
        download_dir: str = "",
    ):
        """Submit a YouTube download task to Celery.

        Falls back to in-process thread if Celery is unavailable.
        """
        settings = get_settings()
        dl_dir = download_dir or settings.DOWNLOAD_DIR
        os.makedirs(dl_dir, exist_ok=True)
        clean_old_files(dl_dir, settings.MAX_FILE_AGE_MINUTES)

        task_name = "youtube.download_audio" if audio_only else "youtube.download_video"
        task_args = [url, quality, dl_dir]

        try:
            # Try Celery
            celery_app.send_task(
                task_name,
                args=task_args,
                task_id=task_id,
                queue="default",
            )
            logger.info("Submitted Celery task %s (%s) -> %s", task_id, task_name, url)
            return
        except Exception as exc:
            logger.warning(
                "Celery unavailable (%s), falling back to thread-based download", exc
            )

        # Fallback: in-process thread
        _fallback_set(task_id, {
            "percent": 0.0,
            "speed": "",
            "eta": "",
            "filename": "",
            "status": "queued",
            "error_msg": "",
            "output_path": "",
        })

        thread = threading.Thread(
            target=YouTubeService._fallback_download_thread,
            args=(task_id, url, quality, audio_only, dl_dir),
            daemon=True,
        )
        thread.start()

    @staticmethod
    def get_progress(task_id: str) -> dict | None:
        """Get task progress — reads from Redis (Celery) or in-memory fallback."""
        # Try Celery progress (Redis)
        progress = get_celery_progress(task_id)
        if progress is not None:
            return progress
        # Fallback: in-memory
        return _fallback_get(task_id)

    @staticmethod
    def cancel(task_id: str):
        """Cancel a running download."""
        # Try Celery
        try:
            celery_app.control.revoke(task_id, terminate=True, signal="SIGTERM")
        except Exception:
            pass
        # Also mark fallback
        _fallback_set(task_id, {"status": "cancelled"})
        clear_celery_progress(task_id)

    @staticmethod
    def remove_task(task_id: str):
        """Clean up task state after file is served."""
        _fallback_remove(task_id)
        clear_celery_progress(task_id)

    @staticmethod
    def active_count() -> int:
        try:
            i = celery_app.control.inspect()
            active = i.active() or {}
            return sum(len(tasks) for tasks in active.values())
        except Exception:
            with _tasks_lock:
                return len(_tasks)

    # ── Fallback thread-based download ────────────────────────

    @staticmethod
    def _fallback_download_thread(
        task_id: str,
        url: str,
        quality: str,
        audio_only: bool,
        download_dir: str,
    ):
        """Thread-based download when Celery is unavailable."""
        import yt_dlp
        from app.utils.helpers import apply_cookies, find_ffmpeg

        ffmpeg_path = find_ffmpeg()
        state = _fallback_get(task_id) or {}

        def progress_hook(d: dict):
            nonlocal state
            if d.get("status") == "cancelled":
                raise Exception("Download cancelled by user")
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                state["percent"] = round((downloaded / total * 100), 1) if total > 0 else 0.0
                state["speed"] = d.get("_speed_str", "") or ""
                state["eta"] = d.get("_eta_str", "") or ""
                state["status"] = "downloading"
                state["filename"] = os.path.basename(d.get("filename", ""))
            elif d.get("status") == "finished":
                state["status"] = "processing"
                state["percent"] = 100.0
                state["filename"] = os.path.basename(d.get("filename", ""))
            _fallback_set(task_id, dict(state))

        try:
            prefix = f"yt_{task_id}_"
            outtmpl = os.path.join(download_dir, f"{prefix}%(title)s.%(ext)s")
            opts: dict = {
                "outtmpl": outtmpl,
                "progress_hooks": [progress_hook],
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }
            if ffmpeg_path:
                opts["ffmpeg_location"] = ffmpeg_path
            apply_cookies(opts, download=True)

            if audio_only:
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": __import__("app.tasks.youtube_tasks", fromlist=["_normalize_audio_quality"])._normalize_audio_quality(quality),
                }]
            else:
                quality_map = {
                    "highest": "bestvideo+bestaudio/best",
                    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
                }
                opts["format"] = quality_map.get(quality.lower(), "bestvideo+bestaudio/best")

            os.makedirs(download_dir, exist_ok=True)

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url.strip()])

            # Find output
            from pathlib import Path
            candidates = []
            for p in Path(download_dir).iterdir():
                name = p.name
                if not name.startswith(prefix):
                    continue
                if any(name.endswith(ext) for ext in (".part", ".fragment", ".ytdl")):
                    continue
                if p.is_file():
                    candidates.append(p)
            output_path = str(candidates[0].resolve()) if candidates else ""

            state["output_path"] = output_path
            state["status"] = "done" if output_path else "error"
            state["percent"] = 100.0
            if not output_path:
                state["error_msg"] = "Output file not found after download"
            _fallback_set(task_id, dict(state))

            from app.utils.helpers import save_task_state
            save_task_state(task_id, state, download_dir)

        except Exception as e:
            state["status"] = "error"
            state["error_msg"] = str(e)
            _fallback_set(task_id, dict(state))
            try:
                from app.utils.helpers import save_task_state
                save_task_state(task_id, state, download_dir)
            except Exception:
                pass
