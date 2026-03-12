"""Redis backend for robots.txt cache. Use when WORKER_ROBOTS_CACHE_BACKEND=redis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RedisRobotsCacheBackend:
    """Persist robots cache in Redis. Key: {key_prefix}{origin}, value: body. Optional TTL."""

    def __init__(
        self,
        redis_url: str,
        key_prefix: str = "multi_asset_invest:robots:",
        ttl_sec: int = 86400,
    ) -> None:
        self._redis_url = redis_url
        self._key_prefix = key_prefix
        self._ttl_sec = ttl_sec
        self._client: Any = None

    def _get_client(self):  # noqa: ANN201
        if self._client is None:
            import redis
            self._client = redis.Redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    def load(self) -> dict[str, str]:
        try:
            client = self._get_client()
            pattern = self._key_prefix + "*"
            keys = client.keys(pattern)
            result: dict[str, str] = {}
            for key in keys:
                if not isinstance(key, str):
                    continue
                origin = key[len(self._key_prefix) :]
                val = client.get(key)
                if val is not None:
                    result[origin] = val
            return result
        except Exception as e:
            logger.warning("Redis robots cache load failed: %s", e)
            return {}

    def save(self, cache: dict[str, str]) -> None:
        if not cache:
            return
        try:
            client = self._get_client()
            pipe = client.pipeline()
            for origin, body in cache.items():
                key = self._key_prefix + origin
                if self._ttl_sec > 0:
                    pipe.setex(key, self._ttl_sec, body)
                else:
                    pipe.set(key, body)
            pipe.execute()
        except Exception as e:
            logger.warning("Redis robots cache save failed: %s", e)
