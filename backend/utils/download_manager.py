import threading
import time
import uuid
from pathlib import Path
from typing import Any

from utils.config import get_settings
from utils.temp_files import create_download_directory, remove_directory


class TaskCancelledError(Exception):
    """Raised inside the download thread when a task has been cancelled."""
    pass


class DownloadTask:
    """Represents a single download task tracked entirely in memory."""

    def __init__(self, task_id: str, directory: Path) -> None:
        self.task_id = task_id
        self.directory = directory
        self.status: str = "queued"
        self.progress: float = 0.0
        self.speed: str = ""
        self.eta: str = ""
        self.filename: str = ""
        self.file_path: Path | None = None
        self.error_msg: str | None = None
        self.download_url: str | None = None
        self.created_at: float = time.time()
        self._cancelled = threading.Event()

    def cancel(self) -> None:
        self._cancelled.set()
        self.status = "cancelled"

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled.is_set()

    def to_dict(self, base_url: str = "") -> dict[str, Any]:
        result: dict[str, Any] = {
            "percent": self.progress,
            "speed": self.speed,
            "eta": self.eta,
            "filename": self.filename,
            "status": self.status,
            "error_msg": self.error_msg or "",
        }
        if self.download_url:
            result["download_url"] = self.download_url
        elif self.status == "done" and self.task_id:
            result["download_url"] = f"{base_url}/api/youtube/file/{self.task_id}"
        return result


class DownloadManager:
    """In-memory task manager. Thread-safe, no persistence."""

    def __init__(self) -> None:
        self._tasks: dict[str, DownloadTask] = {}
        self._lock = threading.Lock()

    def create_task(self) -> DownloadTask:
        task_id = uuid.uuid4().hex
        settings = get_settings()
        directory = create_download_directory(settings.temp_dir)
        task = DownloadTask(task_id, directory)
        with self._lock:
            self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> DownloadTask | None:
        with self._lock:
            return self._tasks.get(task_id)

    def remove_task(self, task_id: str) -> None:
        with self._lock:
            task = self._tasks.pop(task_id, None)
            if task:
                remove_directory(task.directory)

    def cleanup_expired(self) -> None:
        settings = get_settings()
        cutoff = time.time() - settings.download_token_ttl_seconds
        with self._lock:
            expired = [tid for tid, t in self._tasks.items() if t.created_at < cutoff]
            for tid in expired:
                task = self._tasks.pop(tid)
                remove_directory(task.directory)


manager = DownloadManager()
