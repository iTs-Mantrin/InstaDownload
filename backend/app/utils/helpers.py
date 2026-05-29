"""Shared utility functions."""

import os
import re
import uuid
import time
import glob
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def sanitize_filename(name: str) -> str:
    """Remove characters invalid in filenames."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.strip(". ")
    return name or "download"


def format_file_size(bytes_size: float) -> str:
    """Human-readable file size."""
    if bytes_size <= 0:
        return "Unknown"
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def format_eta(seconds: float) -> str:
    """Seconds to MM:SS or HH:MM:SS."""
    if seconds <= 0:
        return "--:--"
    s = int(seconds)
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    if h > 0:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"


def is_youtube_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    domain = parsed.netloc.lower()
    return any(d in domain for d in ["youtube.com", "youtu.be", "m.youtube.com"])


def is_instagram_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    domain = parsed.netloc.lower()
    return "instagram.com" in domain


def is_valid_url(url: str) -> bool:
    if not url or not url.strip():
        return False
    parsed = urlparse(url.strip())
    return bool(parsed.netloc) and bool(parsed.scheme)


def generate_task_id() -> str:
    return uuid.uuid4().hex[:12]


def clean_old_files(directory: str, max_age_minutes: int = 30):
    """Remove files older than max_age_minutes from directory."""
    cutoff = time.time() - (max_age_minutes * 60)
    try:
        for f in Path(directory).iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                try:
                    f.unlink()
                except Exception:
                    pass
    except Exception:
        pass


def find_ffmpeg() -> str | None:
    """Locate ffmpeg binary (same logic as desktop version)."""
    which = shutil.which("ffmpeg")
    if which:
        return which
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Microsoft" / "WinGet" / "Packages"
        / "Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe"
        / "ffmpeg-*" / "bin" / "ffmpeg.exe",
        Path(os.environ.get("PROGRAMFILES", "C:\\Program Files"))
        / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]
    for candidate in candidates:
        pattern = str(candidate)
        matches = glob.glob(pattern)
        if matches:
            return os.path.abspath(matches[0])
        if candidate.exists():
            return str(candidate.resolve())
    try:
        result = subprocess.run(
            ["where", "ffmpeg"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            path = result.stdout.strip().split("\n")[0].strip()
            if path and os.path.isfile(path):
                return path
    except Exception:
        pass
    return None
