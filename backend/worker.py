"""Celery worker entry point — import and expose the Celery app.

Usage:
    celery -A worker.celery worker --loglevel=info
"""

from app.celery_app import celery_app as celery

__all__ = ["celery"]
