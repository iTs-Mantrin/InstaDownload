"""Redis cache client."""

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
