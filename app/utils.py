"""Utility functions for the downloader application."""

import os
import re
import platform
from pathlib import Path
from urllib.parse import urlparse


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are invalid in filenames."""
    invalid = r'[<>:"/\\|?*]'
    name = re.sub(invalid, "_", name)
    name = name.strip(". ")
    return name or "download"


def get_default_download_path() -> str:
    """Return the default downloads directory."""
    return str(Path(__file__).parent.parent / "downloads")


def format_file_size(bytes_size: float) -> str:
    """Format bytes into human-readable string."""
    if bytes_size <= 0:
        return "Unknown"
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def format_eta(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    if seconds <= 0:
        return "--:--"
    secs = int(seconds)
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube link."""
    parsed = urlparse(url.strip())
    domain = parsed.netloc.lower()
    return any(d in domain for d in ["youtube.com", "youtu.be", "m.youtube.com"])


def is_instagram_url(url: str) -> bool:
    """Check if URL is an Instagram link."""
    parsed = urlparse(url.strip())
    domain = parsed.netloc.lower()
    return "instagram.com" in domain


def is_valid_url(url: str) -> bool:
    """Basic URL validation."""
    url = url.strip()
    if not url:
        return False
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def open_folder(path: str):
    """Open the given folder in the file explorer."""
    path = os.path.normpath(path)
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            import subprocess
            subprocess.Popen(["open", path])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass
