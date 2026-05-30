from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.downloader import router as downloader_router
from routes.instagram import router as instagram_router
from routes.youtube import router as youtube_router
from utils.config import get_settings
from utils.download_manager import manager as download_manager
from utils.temp_files import ensure_temp_directory, remove_expired_temp_directories


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_temp_directory()
    remove_expired_temp_directories(settings.temp_dir, settings.download_token_ttl_seconds)
    download_manager.cleanup_expired()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Stateless YouTube downloader API powered by FastAPI, yt-dlp, and FFmpeg.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(downloader_router, prefix="/api", tags=["downloader"])
app.include_router(youtube_router, prefix="/api", tags=["youtube-frontend"])
app.include_router(instagram_router, prefix="/api", tags=["instagram"])


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
