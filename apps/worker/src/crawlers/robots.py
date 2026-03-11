"""Robots.txt fetch and simple rule check (robots.txt-aware)."""

import logging
import re
import urllib.request
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

# Origin -> robots.txt body. Process lifetime; no TTL for now.
_robots_cache: dict[str, str] = {}


def _origin_from_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme or 'https'}://{parsed.netloc}"


def has_cached_robots(origin_or_url: str) -> bool:
    """Return True if robots.txt for this origin is already in cache (no network needed)."""
    return _origin_from_url(origin_or_url) in _robots_cache


def fetch_robots_txt(base_url: str, timeout: int = 10) -> str:
    """Fetch robots.txt for base_url (e.g. https://example.com). Returns empty string on failure.
    Results are cached per origin; cache hit returns immediately without network."""
    origin = _origin_from_url(base_url)
    if origin in _robots_cache:
        logger.debug("Robots cache hit for origin=%s", origin)
        return _robots_cache[origin]
    robots_url = urljoin(origin + "/", "robots.txt")
    logger.debug("Fetching robots.txt: %s", robots_url)
    try:
        req = urllib.request.Request(
            robots_url, headers={"User-Agent": "MultiAssetInvestWorker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            logger.debug("Fetched robots.txt from %s (%d bytes)", robots_url, len(body))
            _robots_cache[origin] = body
            return body
    except Exception as e:
        logger.warning("Failed to fetch robots.txt from %s: %s", robots_url, e)
        _robots_cache[origin] = ""
        return ""


def parse_crawl_delay(robots_txt: str) -> float | None:
    """Parse Crawl-delay (non-standard) from User-agent: * section. Returns seconds or None."""
    if not robots_txt or not robots_txt.strip():
        return None
    lines = robots_txt.strip().splitlines()
    in_global = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if re.match(r"User-agent:\s*\*", line, re.I):
            in_global = True
            continue
        if in_global and re.match(r"User-agent:", line, re.I):
            in_global = False
            continue
        if in_global:
            m = re.match(r"Crawl-delay:\s*([\d.]+)", line, re.I)
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    pass
    return None


def _disallow_paths(robots_txt: str) -> list[str]:
    """Parse Disallow lines for User-agent: *. Returns path prefixes to disallow."""
    lines = robots_txt.strip().splitlines()
    paths: list[str] = []
    in_global = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if re.match(r"User-agent:\s*\*", line, re.I):
            in_global = True
            continue
        if in_global and re.match(r"User-agent:", line, re.I):
            in_global = False
            continue
        if in_global:
            m = re.match(r"Disallow:\s*(.+)", line, re.I)
            if m:
                path = m.group(1).strip()
                if path:
                    paths.append(path)
    return paths


def can_fetch(url: str, robots_txt: str) -> bool:
    """Return True if url is allowed by robots.txt. If robots_txt is empty, allow (no robots)."""
    if not robots_txt.strip():
        logger.debug("No robots.txt content, allowing url=%s", url)
        return True
    parsed = urlparse(url)
    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path
    for disallow in _disallow_paths(robots_txt):
        if disallow.startswith("/") and path.startswith(disallow):
            logger.info("robots.txt disallows url=%s (path %s matches Disallow: %s)", url, path, disallow)
            return False
        if not disallow.startswith("/") and disallow in path:
            logger.info("robots.txt disallows url=%s (path %s contains %s)", url, path, disallow)
            return False
    logger.debug("robots.txt allows url=%s", url)
    return True
