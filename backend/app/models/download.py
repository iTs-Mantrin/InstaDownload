"""SQLAlchemy ORM model for download tracking."""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DownloadRecord(Base):
    __tablename__ = "downloads"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False)  # youtube / instagram
    url: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=""
    )  # video / audio / story / profile_pic
    quality: Mapped[str] = mapped_column(String(16), nullable=False, default="highest")
    audio_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="queued"
    )  # queued / downloading / done / error
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=True, default=0)
    error_msg: Mapped[str] = mapped_column(Text, nullable=True, default="")
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True, default="")
    user_agent: Mapped[str] = mapped_column(String(256), nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
