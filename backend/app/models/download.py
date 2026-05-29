"""SQLAlchemy models for InstaDownload."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class DownloadRecord(Base):
    __tablename__ = "downloads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(24), unique=True, nullable=False, index=True)
    source = Column(String(20), nullable=False)  # youtube / instagram
    url = Column(Text, nullable=False)
    status = Column(String(20), default="queued")  # queued/downloading/done/error
    file_path = Column(Text, nullable=True)
    file_size = Column(Integer, nullable=True)
    title = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
