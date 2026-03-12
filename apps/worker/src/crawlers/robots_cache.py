"""Robots.txt cache backends: file (JSON) and optional Redis. Persist across restarts."""

import json
import logging
import os
from typing import Protocol

logger = logging.getLogger(__name__)


class RobotsCacheBackend(Protocol):
    """Protocol for robots cache persistence: load/save full cache dict."""

    def load(self) -> dict[str, str]:
        """Load full cache (origin -> robots body). Return {} on failure."""
        ...

    def save(self, cache: dict[str, str]) -> None:
        """Persist full cache."""
        ...


class FileRobotsCacheBackend:
    """Persist robots cache as a single JSON file. Atomic write via temp file + replace."""

    def __init__(self, path: str) -> None:
        self._path = path

    def load(self) -> dict[str, str]:
        if not os.path.isfile(self._path):
            return {}
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return {k: str(v) for k, v in data.items()}
            return {}
        except Exception as e:
            logger.warning("Failed to load robots cache from %s: %s", self._path, e)
            return {}

    def save(self, cache: dict[str, str]) -> None:
        try:
            dirname = os.path.dirname(self._path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=0)
            os.replace(tmp, self._path)
        except Exception as e:
            logger.warning("Failed to save robots cache to %s: %s", self._path, e)


def get_backend() -> RobotsCacheBackend:
    """Return the configured cache backend (file or redis)."""
    from config import settings

    backend = (settings.robots_cache_backend or "file").strip().lower()
    if backend == "redis":
        return _get_redis_backend()
    return FileRobotsCacheBackend(settings.robots_cache_path)


def _get_redis_backend() -> RobotsCacheBackend:
    try:
        from crawlers.robots_cache_redis import RedisRobotsCacheBackend
        from config import settings

        return RedisRobotsCacheBackend(
            redis_url=settings.redis_url,
            key_prefix="multi_asset_invest:robots:",
            ttl_sec=86400,
        )
    except ImportError:
        logger.warning("Redis robots cache backend not available, falling back to file")
        from config import settings

        return FileRobotsCacheBackend(settings.robots_cache_path)
