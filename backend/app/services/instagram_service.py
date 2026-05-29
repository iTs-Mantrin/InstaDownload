"""Instagram download service using yt-dlp."""

import os
import threading
import re
from pathlib import Path
from typing import Optional

import yt_dlp

from app.utils.helpers import find_ffmpeg, snapshot_directory, find_new_output, save_task_state

_FFMPEG_PATH = find_ffmpeg()

_tasks: dict[str, dict] = {}
_tasks_lock = threading.Lock()


def _get_state(task_id: str) -> dict:
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
            }
        return _tasks[task_id]


def _progress_hook(state: dict):
    def hook(d: dict):
        if state["status"] == "cancelled":
            raise Exception("Download cancelled")
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


class InstagramService:
    """Handles Instagram post/reel/story/profile downloads."""

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
        """Preview Instagram media metadata."""
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }
            if _FFMPEG_PATH:
                opts["ffmpeg_location"] = _FFMPEG_PATH
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    media_type = "post"
                    if "/reel/" in url:
                        media_type = "reel"
                    elif info.get("entries") and len(info["entries"]) > 1:
                        media_type = "carousel"
                    return {
                        "title": info.get("title", "Instagram media"),
                        "type": media_type,
                        "thumbnail": info.get("thumbnail", ""),
                        "username": info.get("uploader", ""),
                        "description": (info.get("description") or "")[:200],
                    }
        except Exception:
            return None
        return None

    @staticmethod
    def start_download(
        task_id: str,
        url: str,
        download_dir: str = "",
    ):
        """Download Instagram post/reel in background."""
        state = _get_state(task_id)
        thread = threading.Thread(
            target=InstagramService._download_thread,
            args=(state, task_id, url, download_dir),
            daemon=True,
        )
        thread.start()

    @staticmethod
    def start_story_download(
        task_id: str,
        username: str,
        download_dir: str = "",
    ):
        """Try to download Instagram stories for a username."""
        state = _get_state(task_id)
        thread = threading.Thread(
            target=InstagramService._story_thread,
            args=(state, task_id, username, download_dir),
            daemon=True,
        )
        thread.start()

    @staticmethod
    def download_profile_pic(username: str, download_dir: str = "") -> str | None:
        """Download Instagram profile picture, returns file path or None."""
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(profile_url, download=False)
                if info and info.get("thumbnail"):
                    import requests
                    thumb_url = info["thumbnail"]
                    # Try HD version
                    hd_url = thumb_url.replace("/s150x150/", "/s1080x1080/")
                    try:
                        r = requests.get(hd_url, timeout=10)
                        if r.status_code == 200:
                            ext = "jpg"
                            path = os.path.join(download_dir, f"{username}_profile.{ext}")
                            with open(path, "wb") as f:
                                f.write(r.content)
                            return path
                    except Exception:
                        pass
                    # Fallback to original thumbnail
                    try:
                        r = requests.get(thumb_url, timeout=10)
                        if r.status_code == 200:
                            path = os.path.join(download_dir, f"{username}_profile.jpg")
                            with open(path, "wb") as f:
                                f.write(r.content)
                            return path
                    except Exception:
                        pass
        except Exception:
            pass
        return None

    @staticmethod
    def _download_thread(
        state: dict,
        task_id: str,
        url: str,
        download_dir: str,
    ):
        try:
            outtmpl = os.path.join(download_dir, "ig_%(id)s_%(title)s.%(ext)s")
            opts = {
                "format": "best",
                "outtmpl": outtmpl,
                "progress_hooks": [_progress_hook(state)],
                "quiet": True,
                "no_warnings": True,
            }
            if _FFMPEG_PATH:
                opts["ffmpeg_location"] = _FFMPEG_PATH

            # Snapshot before so we can detect the new output file
            before = snapshot_directory(download_dir)

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url.strip()])

            output_path = find_new_output(before, download_dir)
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

    @staticmethod
    def _story_thread(
        state: dict,
        task_id: str,
        username: str,
        download_dir: str,
    ):
        """Attempt story download (requires cookies in production)."""
        try:
            story_url = f"https://www.instagram.com/stories/{username}/"
            outtmpl = os.path.join(download_dir, "story_%(id)s_%(title)s.%(ext)s")
            opts = {
                "format": "best",
                "outtmpl": outtmpl,
                "progress_hooks": [_progress_hook(state)],
                "quiet": True,
                "no_warnings": True,
                "cookiefrombrowser": ("chrome", "edge"),
                "ignoreerrors": True,
            }
            if _FFMPEG_PATH:
                opts["ffmpeg_location"] = _FFMPEG_PATH

            before = snapshot_directory(download_dir)

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(story_url, download=True)

            if info and info.get("entries"):
                output_path = find_new_output(before, download_dir)
                state["output_path"] = output_path
                state["status"] = "done" if output_path else "error"
                state["percent"] = 100.0
                state["before_snapshot"] = list(before)
                state["new_files"] = [output_path] if output_path else []
                if not output_path:
                    state["error_msg"] = "Stories output file not found"
            else:
                state["status"] = "error"
                state["error_msg"] = (
                    "No stories found or requires login. "
                    "Try adding cookies via YT_DLP_COOKIES_FILE env var."
                )
            state["before_snapshot"] = list(before)
            state["new_files"] = []
            save_task_state(task_id, state, download_dir)

        except Exception as e:
            state["status"] = "error"
            state["error_msg"] = str(e)
            state["before_snapshot"] = list(before)
            state["new_files"] = []
            save_task_state(task_id, state, download_dir)


