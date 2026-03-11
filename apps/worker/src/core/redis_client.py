"""Redis connection for queue (worker)."""

from redis.asyncio import Redis

from config import settings

# Queue key for jobs (e.g. crawl, extract, signal)
QUEUE_JOBS = "multi_asset_invest:queue:jobs"


def get_redis() -> Redis:
    """Return Redis client for queue (cache if needed)."""
    return Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
