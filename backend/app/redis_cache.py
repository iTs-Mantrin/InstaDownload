"""Redis cache client and caching utilities."""

import json
from redis.asyncio import Redis
from app.config import get_settings

settings = get_settings()

redis_client: Redis | None = None


async def get_redis() -> Redis | None:
    """Get or create the Redis connection."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = Redis.from_url(
                settings.REDIS_URL, decode_responses=True, socket_timeout=2
            )
        except Exception:
            return None
    return redis_client


async def close_redis():
    """Close Redis connection on shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


# ── Cache helpers ──────────────────────────────────────────────

async def cache_get(key: str) -> dict | None:
    """Get JSON value from cache."""
    r = await get_redis()
    if not r:
        return None
    try:
        data = await r.get(f"cache:{key}")
        return json.loads(data) if data else None
    except Exception:
        return None


async def cache_set(key: str, value: dict, ttl: int = 300) -> bool:
    """Set JSON value in cache with TTL (default 5 min)."""
    r = await get_redis()
    if not r:
        return False
    try:
        await r.setex(f"cache:{key}", ttl, json.dumps(value))
        return True
    except Exception:
        return False


async def cache_delete(key: str) -> bool:
    """Delete a cache key."""
    r = await get_redis()
    if not r:
        return False
    try:
        await r.delete(f"cache:{key}")
        return True
    except Exception:
        return False


# ── Preview cache ──────────────────────────────────────────────

PREVIEW_CACHE_TTL = 600  # 10 minutes

async def get_cached_preview(url: str) -> dict | None:
    """Get cached preview metadata for a URL."""
    from hashlib import sha256
    key = f"preview:{sha256(url.encode()).hexdigest()}"
    return await cache_get(key)


async def set_cached_preview(url: str, data: dict) -> bool:
    """Cache preview metadata for a URL."""
    from hashlib import sha256
    key = f"preview:{sha256(url.encode()).hexdigest()}"
    return await cache_set(key, data, ttl=PREVIEW_CACHE_TTL)
