"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import youtube, instagram, utilities, analytics, unified
from app.services.cleanup_service import CleanupService

settings = get_settings()

# Ensure download directory
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await CleanupService.start()
    yield
    CleanupService.stop()


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
app.include_router(utilities.router)
app.include_router(analytics.router)
app.include_router(unified.router)

# ── Serve built frontend (production) ───────────────────────
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets",
    )

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(str(FRONTEND_DIST / "index.html"))

    # SEO endpoints — must come before the SPA catch-all
    @app.get("/robots.txt", include_in_schema=False)
    async def robots():
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            "User-agent: *\nAllow: /\nSitemap: https://instadownload.app/sitemap.xml\n"
        )

    @app.get("/sitemap.xml", include_in_schema=False)
    async def sitemap():
        from fastapi.responses import XMLResponse
        return XMLResponse(
            content="""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://instadownload.app/</loc><priority>1.0</priority></url>
  <url><loc>https://instadownload.app/youtube</loc><priority>0.9</priority></url>
  <url><loc>https://instadownload.app/instagram</loc><priority>0.9</priority></url>
</urlset>"""
        )

    @app.get("/{path:path}", include_in_schema=False)
    async def serve_spa(path: str):
        """SPA fallback — serve index.html for all non-API routes."""
        fp = FRONTEND_DIST / path
        if fp.exists() and fp.is_file():
            return FileResponse(str(fp))
        return FileResponse(str(FRONTEND_DIST / "index.html"))


# ── Main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
