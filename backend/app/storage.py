"""Storage abstraction — Local filesystem or S3.

Configured via ``STORAGE_BACKEND`` env var:
  - ``local`` (default) — files stored in DOWNLOAD_DIR
  - ``s3`` — files uploaded to S3, presigned URL returned
"""

from __future__ import annotations

import os
import abc
import logging
from pathlib import Path
from typing import BinaryIO

from app.config import get_settings

logger = logging.getLogger(__name__)


class StorageBackend(abc.ABC):
    """Abstract storage backend for completed downloads."""

    @abc.abstractmethod
    def store(self, local_path: str, remote_key: str | None = None) -> str:
        """Persist *local_path* to storage.

        Returns the public URL or local path the file is accessible at.
        If *remote_key* is None the filename is derived from *local_path*.
        """
        ...

    @abc.abstractmethod
    def get_download_url(self, remote_key: str, filename: str) -> str:
        """Return a download URL (direct or presigned) for *remote_key*."""
        ...

    @abc.abstractmethod
    def cleanup(self, remote_key: str) -> None:
        """Remove a file from storage."""
        ...


class LocalStorage(StorageBackend):
    """Files remain in DOWNLOAD_DIR — no copying needed."""

    def store(self, local_path: str, remote_key: str | None = None) -> str:
        return local_path

    def get_download_url(self, remote_key: str, filename: str) -> str:
        # The local path *is* the storage path already
        return remote_key

    def cleanup(self, remote_key: str) -> None:
        try:
            if os.path.isfile(remote_key):
                os.remove(remote_key)
        except Exception:
            pass


class S3Storage(StorageBackend):
    """Upload files to S3 and return presigned download URLs."""

    def __init__(self) -> None:
        settings = get_settings()
        self.bucket = settings.S3_BUCKET_NAME
        self.region = settings.S3_REGION
        self.access_key = settings.AWS_ACCESS_KEY_ID
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.presign_ttl = settings.S3_PRESIGN_TTL
        self._client = None

    @property
    def _s3_client(self):
        if self._client is None:
            import boto3
            kwargs = {
                "aws_access_key_id": self.access_key,
                "aws_secret_access_key": self.secret_key,
                "region_name": self.region,
            }
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._client = boto3.client("s3", **kwargs)
        return self._client

    def store(self, local_path: str, remote_key: str | None = None) -> str:
        if remote_key is None:
            remote_key = os.path.basename(local_path)
        logger.info("Uploading %s to s3://%s/%s", local_path, self.bucket, remote_key)
        self._s3_client.upload_file(local_path, self.bucket, remote_key)
        # Return the key — caller can pass it back for presigned URL
        return remote_key

    def get_download_url(self, remote_key: str, filename: str) -> str:
        from urllib.parse import quote
        safe_filename = quote(filename)
        return self._s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": remote_key,
                "ResponseContentDisposition": f'attachment; filename="{safe_filename}"',
            },
            ExpiresIn=self.presign_ttl,
        )

    def cleanup(self, remote_key: str) -> None:
        try:
            self._s3_client.delete_object(Bucket=self.bucket, Key=remote_key)
        except Exception:
            pass


# ── Factory ──────────────────────────────────────────────────

_STORAGE: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Return the configured storage backend singleton."""
    global _STORAGE
    if _STORAGE is not None:
        return _STORAGE

    settings = get_settings()
    backend = settings.STORAGE_BACKEND.lower()
    if backend == "s3":
        _STORAGE = S3Storage()
    else:
        _STORAGE = LocalStorage()
    logger.info("Storage backend: %s", type(_STORAGE).__name__)
    return _STORAGE


def reset_storage():
    """Reset singleton (useful for tests)."""
    global _STORAGE
    _STORAGE = None
