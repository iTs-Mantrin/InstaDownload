"""Download engine using yt-dlp Python API with progress hooks."""

import os
import shutil
import threading
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional, Callable

import yt_dlp


def _find_ffmpeg() -> str | None:
    """Locate ffmpeg binary on the system. Returns path or None."""
    # 1 — Check PATH
    which = shutil.which("ffmpeg")
    if which:
        return which

    # 2 — Common Windows install locations
    candidates = [
        # Winget install (Gyan)
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Microsoft" / "WinGet" / "Packages"
        / "Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe"
        / "ffmpeg-*" / "bin" / "ffmpeg.exe",
        # Program Files
        Path(os.environ.get("PROGRAMFILES", "C:\\Program Files"))
        / "ffmpeg" / "bin" / "ffmpeg.exe",
        Path(os.environ.get("PROGRAMFILES(x86)", "C:\\Program Files (x86)"))
        / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]

    for candidate in candidates:
        # Expand wildcard for winget version folder
        parent = candidate.parent.parent.parent if "WinGet" in str(candidate) else None
        if parent and "WinGet" in str(candidate):
            # Resolve ffmpeg-* wildcard
            pattern = str(candidate)
            import glob
            matches = glob.glob(pattern)
            if matches:
                return os.path.abspath(matches[0])

        if candidate.exists():
            return str(candidate.resolve())

    # 3 — Windows Registry (via where.exe)
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


# Discover ffmpeg once at module load
_FFMPEG_PATH = _find_ffmpeg()


class DownloadType(Enum):
    VIDEO = "video"
    AUDIO = "audio"


class InstagramType(Enum):
    POST_REEL = "post_reel"
    STORY = "story"


class DownloadStatus:
    """Holds the current progress state for a download."""

    def __init__(self):
        self.percent = 0.0
        self.speed = ""
        self.eta = ""
        self.filename = ""
        self.status = "idle"  # idle | downloading | processing | done | error
        self.error_msg = ""


ProgressCallback = Callable[[DownloadStatus], None]


class Downloader:
    """Wrapper around yt-dlp for YouTube and Instagram downloads."""

    def __init__(self, download_path: str, progress_callback: Optional[ProgressCallback] = None):
        self.download_path = download_path
        self.progress_callback = progress_callback
        self._cancel_flag = threading.Event()

    def _progress_hook(self, d: dict):
        """yt-dlp progress hook — updates DownloadStatus."""
        status = DownloadStatus()

        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            status.percent = (downloaded / total * 100) if total > 0 else 0.0
            status.speed = d.get("_speed_str", "") or ""
            status.eta = d.get("_eta_str", "") or ""
            status.status = "downloading"
            status.filename = os.path.basename(d.get("filename", ""))
        elif d.get("status") == "finished":
            status.status = "processing"
            status.percent = 100.0
            status.filename = os.path.basename(d.get("filename", ""))
        elif d.get("status") == "error":
            status.status = "error"
            status.error_msg = str(d.get("error", "Unknown error"))

        if self.progress_callback:
            self.progress_callback(status)

    def _make_opts(self, extra: dict) -> dict:
        """Base options dict with common settings."""
        opts = {
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "ignoreerrors": False,
            # When merging video+audio (bv*+ba), always produce mp4
            "merge_output_format": "mp4",
        }
        if _FFMPEG_PATH:
            opts["ffmpeg_location"] = _FFMPEG_PATH
        opts.update(extra)
        return opts

    def cancel(self):
        """Signal cancellation."""
        self._cancel_flag.set()

    # ── YouTube ──────────────────────────────────────────────

    def download_youtube(self, url: str, dl_type: DownloadType, quality: str = "best"):
        """Download YouTube video or audio in a background thread."""
        self._cancel_flag.clear()

        def _run():
            try:
                if dl_type == DownloadType.AUDIO:
                    opts = self._make_opts({
                        "format": "bestaudio/best",
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }],
                        "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
                    })
                else:
                    fmt = self._resolve_youtube_format(quality)
                    opts = self._make_opts({
                        "format": fmt,
                        "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
                    })

                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url.strip()])

                final = DownloadStatus()
                final.status = "done"
                if self.progress_callback:
                    self.progress_callback(final)

            except Exception as e:
                err = DownloadStatus()
                err.status = "error"
                err.error_msg = str(e)
                if self.progress_callback:
                    self.progress_callback(err)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    @staticmethod
    def _resolve_youtube_format(quality: str) -> str:
        """Map quality label to yt-dlp format string.

        Uses bv*+ba (best video any codec + best audio) merged via ffmpeg,
        falling back to a single combined stream. No container restrictions:
        many YouTube streams at 1080p+ use vp9/webm, not h264/mp4.
        """
        mapping = {
            "Highest": "bv*+ba/b",
            "1080p": "bv*[height<=1080]+ba/b[height<=1080]/b",
            "720p": "bv*[height<=720]+ba/b[height<=720]/b",
            "480p": "bv*[height<=480]+ba/b[height<=480]/b",
            "360p": "bv*[height<=360]+ba/b[height<=360]/b",
        }
        return mapping.get(quality, "bv*+ba/b")

    # ── Instagram ────────────────────────────────────────────

    def download_instagram(self, url: str, ig_type: InstagramType):
        """Download Instagram post/reel or story."""
        self._cancel_flag.clear()

        def _run():
            try:
                if ig_type == InstagramType.STORY:
                    # Stories need cookie support; try with common options
                    opts = self._make_opts({
                        "format": "best",
                        "outtmpl": os.path.join(self.download_path,
                                                 "ig_%(id)s_%(title)s.%(ext)s"),
                    })
                else:
                    opts = self._make_opts({
                        "format": "best",
                        "outtmpl": os.path.join(self.download_path,
                                                 "ig_%(id)s_%(title)s.%(ext)s"),
                    })

                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url.strip()])

                final = DownloadStatus()
                final.status = "done"
                if self.progress_callback:
                    self.progress_callback(final)

            except Exception as e:
                err = DownloadStatus()
                err.status = "error"
                err.error_msg = str(e)
                if self.progress_callback:
                    self.progress_callback(err)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    # ── Instagram User Media Listing ─────────────────────────

    @staticmethod
    def list_user_media(username: str) -> tuple[list[dict], str]:
        """Fetch media items for an Instagram user's profile.

        Returns (items, error_message).
          items:      list of dicts with keys title, url, thumbnail, id
          error_msg:  empty string on success, yt-dlp error otherwise

        Tries two approaches:
          1. Direct profile extraction (no auth).
          2. Fallback with browser cookies (Chrome / Edge) if #1 fails.
        """
        results: list[dict] = []
        error_msg = ""
        profile_url = f"https://www.instagram.com/{username}/"

        def _process_entries(info) -> list[dict]:
            """Extract media entries from yt-dlp result."""
            out: list[dict] = []
            if not info or "entries" not in info:
                return out
            for entry in info["entries"]:
                if not entry:
                    continue
                url = entry.get("webpage_url") or entry.get("url") or ""
                if url and not url.startswith("http"):
                    url = f"https://www.instagram.com/p/{url.strip('/')}/"

                title = entry.get("title", "Untitled")
                if title:
                    title = title.split("\n")[0].strip()
                    if len(title) > 80:
                        title = title[:77] + "..."

                out.append({
                    "title": title or "Untitled",
                    "url": url,
                    "thumbnail": entry.get("thumbnail", ""),
                    "id": entry.get("id", ""),
                })
            return out

        # -- Attempt 1: no cookies --
        try:
            with yt_dlp.YoutubeDL({
                "quiet": True, "no_warnings": True,
                "extract_flat": True, "ignoreerrors": False,
            }) as ydl:
                info = ydl.extract_info(profile_url, download=False)
            results = _process_entries(info)
            if results:
                return results, ""
        except Exception as e:
            error_msg = str(e)

        # -- Attempt 2: try with browser cookies (Chrome, then Edge) --
        for browser in ("chrome", "edge", "firefox"):
            try:
                with yt_dlp.YoutubeDL({
                    "quiet": True, "no_warnings": True,
                    "extract_flat": True, "ignoreerrors": True,
                    "cookiesfrombrowser": (browser,),
                }) as ydl:
                    info = ydl.extract_info(profile_url, download=False)
                results = _process_entries(info)
                if results:
                    return results, ""
            except Exception:
                continue

        return results, error_msg

    # ── Info extraction (for URL validation / preview) ───────

    def extract_info(self, url: str) -> Optional[dict]:
        """Extract video/page info without downloading. Returns dict or None."""
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return {
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", info.get("channel", "Unknown")),
                        "webpage_url": info.get("webpage_url", url),
                        "thumbnail": info.get("thumbnail", ""),
                    }
        except Exception:
            return None
        return None
