"""Async SQLAlchemy engine and session factory for Supabase PostgreSQL."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    pass


import logging
logger = logging.getLogger(__name__)


async def init_db():
    """Create async engine and session factory if DATABASE_URL is set.

    Table creation (``metadata.create_all``) is wrapped in a try/except
    so that a transient database outage does **not** crash the application
    during startup.  Query-time errors will still surface naturally.
    """
    global engine, async_session_factory

    if not settings.db_configured:
        return  # No database configured — run without persistence

    # Ensure async driver scheme for SQLAlchemy async
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args={"timeout": 10},
    )

    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create tables (non-fatal on failure)
    try:
        async with engine.begin() as conn:
            from app.models.download import DownloadRecord  # noqa: F401 — register model
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified / created.")
    except Exception as exc:
        logger.warning(
            "Database unreachable during startup — running without DB persistence. Error: %s",
            exc,
        )
        # Engine is still created; if the DB comes back later, queries
        # that use ``get_session`` will error with a clear message.


async def close_db():
    """Dispose of the engine on shutdown."""
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def get_session() -> AsyncSession | None:
    """Get a new async session, or None if DB not configured."""
    global async_session_factory
    if async_session_factory is None:
        return None
    return async_session_factory()
