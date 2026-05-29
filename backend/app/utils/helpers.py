"""Shared utility functions."""

import os
import re
import json
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


# ── Download output helpers ───────────────────────────────────


def snapshot_directory(directory: str) -> set[str]:
    """Return set of filenames in directory (empty if doesn't exist)."""
    try:
        return {p.name for p in Path(directory).iterdir()}
    except Exception:
        return set()


def find_new_output(
    before: set[str], download_dir: str, suffix: str = ""
) -> str:
    """Find the newest completed file in download_dir that wasn't in `before`.

    Filters out .part / .fragment / .ytdl temp files.
    If suffix is set (e.g. '.mp4'), only files ending with that suffix match.
    Returns absolute path string, or '' if nothing found.
    """
    try:
        after = set()
        for p in Path(download_dir).iterdir():
            name = p.name
            # Skip temp files
            if any(name.endswith(ext) for ext in (".part", ".fragment", ".ytdl")):
                continue
            after.add(name)

        new_names = after - before
        candidates = []
        for name in new_names:
            fp = Path(download_dir) / name
            if fp.is_file():
                if suffix and not name.endswith(suffix):
                    continue
                candidates.append(fp)

        if not candidates:
            return ""

        candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return str(candidates[0].resolve())
    except Exception:
        return ""


def save_task_state(task_id: str, state: dict, download_dir: str):
    """Persist completed task state to disk so it survives container restarts."""
    persist = {
        "status": state.get("status", ""),
        "output_path": state.get("output_path", ""),
        "filename": state.get("filename", ""),
        "before_snapshot": list(state.get("before_snapshot", [])),
        "new_files": list(state.get("new_files", [])),
        "percent": state.get("percent", 0.0),
        "error_msg": state.get("error_msg", ""),
    }
    try:
        os.makedirs(download_dir, exist_ok=True)
        task_file = os.path.join(download_dir, f".task_{task_id}.json")
        with open(task_file, "w") as f:
            json.dump(persist, f, indent=2)
    except Exception:
        pass


def load_task_state(task_id: str, download_dir: str) -> dict | None:
    """Recover completed task state from disk marker."""
    task_file = os.path.join(download_dir, f".task_{task_id}.json")
    try:
        with open(task_file) as f:
            return json.load(f)
    except Exception:
        return None
