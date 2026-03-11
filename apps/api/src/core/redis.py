"""Redis client for cache and queue. Use in FastAPI Depends or app state."""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from core.config import settings

_redis: Redis | None = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Yield async Redis connection for request scope (cache + queue)."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    yield _redis


async def close_redis() -> None:
    """Close Redis connection (call on shutdown)."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
