import shutil
import time
import uuid
from pathlib import Path


def ensure_temp_directory() -> Path:
    from utils.config import get_settings

    directory = get_settings().temp_dir
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def create_download_directory(base_directory: Path) -> Path:
    base_directory.mkdir(parents=True, exist_ok=True)
    target = base_directory / uuid.uuid4().hex
    target.mkdir(parents=True, exist_ok=False)
    return target


def find_downloaded_file(directory: Path, extension: str) -> Path | None:
    matches = sorted(directory.glob(f"*{extension}"), key=lambda path: path.stat().st_mtime, reverse=True)
    if matches:
        return matches[0]

    all_files = sorted((path for path in directory.iterdir() if path.is_file()), key=lambda path: path.stat().st_mtime, reverse=True)
    return all_files[0] if all_files else None


def remove_directory(directory: Path) -> None:
    if directory.exists():
        shutil.rmtree(directory, ignore_errors=True)


def remove_expired_temp_directories(base_directory: Path, ttl_seconds: int) -> None:
    if not base_directory.exists():
        return

    cutoff = time.time() - ttl_seconds
    for child in base_directory.iterdir():
        if not child.is_dir():
            continue
        if child.stat().st_mtime < cutoff:
            shutil.rmtree(child, ignore_errors=True)
