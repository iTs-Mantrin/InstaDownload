"""Celery application — task queue for async YouTube downloads.

Broker:   Redis
Backend:  Redis (result store)

Run worker:
    celery -A app.celery_app worker --loglevel=info --concurrency=4
"""

from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "instadownload",
    broker=settings.REDIS_CELERY_URL,
    backend=settings.REDIS_CELERY_URL,
    include=["app.tasks.youtube_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Clean up old results after 1 hour
    result_expires=3600,
    # Rate limit: at most 1 download per user per 10 seconds (per-worker)
    task_annotations={
        "app.tasks.youtube_tasks.*": {"rate_limit": "6/m"},
    },
)
