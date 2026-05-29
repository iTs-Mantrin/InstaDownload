"""Service for tracking downloads in PostgreSQL via SQLAlchemy."""

from datetime import datetime, timezone

from sqlalchemy import select, func

from app.database import get_session
from app.models.download import DownloadRecord


async def record_download(
    *,
    task_id: str,
    source: str,
    url: str,
    media_type: str = "",
    quality: str = "highest",
    audio_only: bool = False,
    status: str = "queued",
    ip_address: str = "",
    user_agent: str = "",
) -> int | None:
    """Insert a new download record. Returns record id or None if no DB."""
    session = await get_session()
    if session is None:
        return None

    async with session:
        record = DownloadRecord(
            task_id=task_id,
            source=source,
            url=url,
            media_type=media_type,
            quality=quality,
            audio_only=audio_only,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record.id


async def update_download_status(
    task_id: str,
    status: str,
    *,
    file_size: int | None = None,
    error_msg: str | None = None,
) -> bool:
    """Update a download record by task_id. Returns True if updated."""
    session = await get_session()
    if session is None:
        return False

    async with session:
        result = await session.execute(
            select(DownloadRecord).where(DownloadRecord.task_id == task_id)
        )
        record = result.scalar_one_or_none()
        if record is None:
            return False

        record.status = status
        if status == "done":
            record.completed_at = datetime.now(timezone.utc)
        if file_size is not None:
            record.file_size = file_size
        if error_msg is not None:
            record.error_msg = error_msg

        await session.commit()
        return True


async def get_download_stats() -> dict:
    """Get aggregate download statistics."""
    session = await get_session()
    if session is None:
        return {"total": 0, "youtube": 0, "instagram": 0}

    async with session:
        total = await session.scalar(
            select(func.count(DownloadRecord.id))
        )
        youtube = await session.scalar(
            select(func.count(DownloadRecord.id)).where(
                DownloadRecord.source == "youtube"
            )
        )
        instagram = await session.scalar(
            select(func.count(DownloadRecord.id)).where(
                DownloadRecord.source == "instagram"
            )
        )
        done = await session.scalar(
            select(func.count(DownloadRecord.id)).where(
                DownloadRecord.status == "done"
            )
        )
        failed = await session.scalar(
            select(func.count(DownloadRecord.id)).where(
                DownloadRecord.status == "error"
            )
        )

    return {
        "total": total or 0,
        "youtube": youtube or 0,
        "instagram": instagram or 0,
        "completed": done or 0,
        "failed": failed or 0,
    }
