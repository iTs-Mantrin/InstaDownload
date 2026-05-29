"""Analytics and health routes."""

import time
from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(tags=["Analytics"])
settings = get_settings()

_start_time = time.time()


@router.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "uptime_seconds": int(time.time() - _start_time),
    }


@router.get("/api/stats")
def get_stats():
    """Basic usage statistics (placeholder — requires DB in production)."""
    from app.services.youtube_service import YouTubeService as yt
    from app.services.instagram_service import InstagramService as ig
    return {
        "active_downloads": 0,  # TODO: query DB
    }
