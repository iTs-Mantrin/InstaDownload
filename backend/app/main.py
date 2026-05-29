"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db, close_db
from app.routers import youtube, instagram
from app.services.cleanup_service import CleanupService

settings = get_settings()

# Ensure download directory exists
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    await init_db()
    await CleanupService.start()
    yield
    CleanupService.stop()
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(youtube.router)
app.include_router(instagram.router)


# Health check
@app.get("/api/health")
async def health_check():
    from app.database import engine
    from app.services.download_tracker import get_download_stats

    info: dict = {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "configured" if settings.db_configured else "not configured",
    }
    if settings.db_configured and engine:
        info["stats"] = await get_download_stats()
    return info


# ── Serve built frontend (production) ────────────────────────

FRONTEND_DIST = None
_here = Path(__file__).resolve().parent  # backend/app/
for _p in [_here.parent, _here.parent.parent, _here.parent.parent.parent]:
    candidate = _p / "frontend" / "dist"
    if candidate.is_dir():
        FRONTEND_DIST = candidate
        break

if FRONTEND_DIST and FRONTEND_DIST.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets",
    )

    @app.get("/robots.txt", include_in_schema=False)
    async def robots():
        return PlainTextResponse("User-agent: *\nAllow: /\n")

    @app.get("/{path:path}", include_in_schema=False)
    async def serve_spa(path: str):
        """SPA fallback — serve index.html for non-API routes."""
        fp = FRONTEND_DIST / path
        if fp.exists() and fp.is_file():
            return FileResponse(str(fp))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/", include_in_schema=False)
    async def backend_root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/docs")


# ── Main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
