"""Background tasks for file cleanup and maintenance."""

import asyncio
import shutil
import time
from pathlib import Path
from app.config import get_settings

settings = get_settings()


class CleanupService:
    """Manages background cleanup of old downloaded files."""

    _running = False

    @classmethod
    async def start(cls, interval_seconds: int = 300):
        """Start periodic cleanup loop."""
        if cls._running:
            return
        cls._running = True
        asyncio.create_task(cls._cleanup_loop(interval_seconds))

    @classmethod
    async def _cleanup_loop(cls, interval: int):
        while cls._running:
            try:
                cls._cleanup()
            except Exception:
                pass
            await asyncio.sleep(interval)

    @classmethod
    def stop(cls):
        cls._running = False

    @staticmethod
    def _cleanup():
        """Remove files older than MAX_FILE_AGE_MINUTES."""
        max_age = settings.MAX_FILE_AGE_MINUTES * 60
        cutoff = time.time() - max_age
        download_dir = Path(settings.DOWNLOAD_DIR)
        if not download_dir.exists():
            return
        for f in download_dir.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                try:
                    f.unlink()
                except Exception:
                    pass
