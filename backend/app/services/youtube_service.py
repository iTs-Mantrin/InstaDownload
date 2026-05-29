"""YouTube download service using yt-dlp."""

import os
import threading
from pathlib import Path
from typing import Optional

import yt_dlp

from app.utils.helpers import find_ffmpeg, generate_task_id, snapshot_directory, find_new_output, save_task_state

_FFMPEG_PATH = find_ffmpeg()

# ── In-memory progress tracking ──────────────────────────────

_tasks: dict[str, dict] = {}
_tasks_lock = threading.Lock()


def _get_progress_state(task_id: str) -> dict:
    with _tasks_lock:
        if task_id not in _tasks:
            _tasks[task_id] = {
                "percent": 0.0,
                "speed": "",
                "eta": "",
                "filename": "",
                "status": "queued",
                "error_msg": "",
                "output_path": "",
                "title": "",
                "duration": 0,
                "thumbnail": "",
            }
        return _tasks[task_id]


def _progress_hook(state: dict):
    def hook(d: dict):
        if state["status"] == "cancelled":
            raise Exception("Download cancelled by user")
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            state["percent"] = (downloaded / total * 100) if total > 0 else 0.0
            state["speed"] = d.get("_speed_str", "") or ""
            state["eta"] = d.get("_eta_str", "") or ""
            state["status"] = "downloading"
            state["filename"] = os.path.basename(d.get("filename", ""))
        elif d.get("status") == "finished":
            state["status"] = "processing"
            state["percent"] = 100.0
            state["filename"] = os.path.basename(d.get("filename", ""))

    return hook


class YouTubeService:
    """Handles YouTube video/audio downloads and info extraction."""

    @staticmethod
    def get_progress(task_id: str) -> dict | None:
        with _tasks_lock:
            return _tasks.get(task_id)

    @staticmethod
    def cancel(task_id: str):
        with _tasks_lock:
            if task_id in _tasks:
                _tasks[task_id]["status"] = "cancelled"

    @staticmethod
    def remove_task(task_id: str):
        with _tasks_lock:
            _tasks.pop(task_id, None)

    @staticmethod
    def extract_info(url: str) -> dict | None:
        """Get video metadata without downloading."""
        try:
            opts = {"quiet": True, "no_warnings": True, "extract_flat": False}
            if _FFMPEG_PATH:
                opts["ffmpeg_location"] = _FFMPEG_PATH
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
                    return {
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", info.get("channel", "Unknown")),
                        "thumbnail": info.get("thumbnail", ""),
                        "webpage_url": info.get("webpage_url", url),
                        "formats": formats[:20],  # limit to first 20
                    }
        except Exception:
            return None
        return None

    @staticmethod
    def start_download(
        task_id: str,
        url: str,
        quality: str = "highest",
        audio_only: bool = False,
        download_dir: str = "",
    ):
        """Start YouTube download in background thread."""
        state = _get_progress_state(task_id)
        thread = threading.Thread(
            target=YouTubeService._download_thread,
            args=(state, task_id, url, quality, audio_only, download_dir),
            daemon=True,
        )
        thread.start()

    @staticmethod
    def _resolve_format(quality: str) -> str:
        mapping = {
            "highest": "bv*+ba/b",
            "1080p": "bv*[height<=1080]+ba/b[height<=1080]/b",
            "720p": "bv*[height<=720]+ba/b[height<=720]/b",
            "480p": "bv*[height<=480]+ba/b[height<=480]/b",
            "360p": "bv*[height<=360]+ba/b[height<=360]/b",
        }
        return mapping.get(quality.lower(), "bv*+ba/b")

    @staticmethod
    def _download_thread(
        state: dict,
        task_id: str,
        url: str,
        quality: str,
        audio_only: bool,
        download_dir: str,
    ):
        try:
            outtmpl = os.path.join(download_dir, "%(title)s.%(ext)s")
            opts = {
                "outtmpl": outtmpl,
                "progress_hooks": [_progress_hook(state)],
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }
            if _FFMPEG_PATH:
                opts["ffmpeg_location"] = _FFMPEG_PATH

            if audio_only:
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            else:
                opts["format"] = YouTubeService._resolve_format(quality)

            # Snapshot before so we can detect the new output file
            before = snapshot_directory(download_dir)

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url.strip()])

            output_suffix = ".mp3" if audio_only else ".mp4"
            output_path = find_new_output(before, download_dir, suffix=output_suffix)
            state["output_path"] = output_path
            state["status"] = "done" if output_path else "error"
            state["percent"] = 100.0
            state["before_snapshot"] = list(before)
            state["new_files"] = [output_path] if output_path else []
            if not output_path:
                state["error_msg"] = "Output file not found after download"

            # Persist to disk so state survives container restarts
            save_task_state(task_id, state, download_dir)

        except Exception as e:
            state["status"] = "error"
            state["error_msg"] = str(e)
            state["before_snapshot"] = list(before)
            state["new_files"] = []
            save_task_state(task_id, state, download_dir)


