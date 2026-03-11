"""Stub crawler: fetch base_url page, extract links from body, return items for robots-allowed URLs."""

import logging
import re
import time
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse

from crawlers.robots import (
    can_fetch,
    fetch_robots_txt,
    has_cached_robots,
    parse_crawl_delay,
)

# Stub: single source base URL (e.g. placeholder; real source would be configured).
STUB_SOURCE_BASE_URL = "https://example.com"
STUB_SOURCE_NAME = "stub"

USER_AGENT = "MultiAssetInvestWorker/1.0"
STUB_MAX_LINKS = 20

# Safety: plan constants
DEFAULT_DELAY_SEC = 1.0
CRAWL_DELAY_CAP_SEC = 60
BACKOFF_SEC = 60

logger = logging.getLogger(__name__)


def _origin_from_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme or 'https'}://{p.netloc}"


def _fetch_page(url: str, timeout: int = 10) -> str:
    """Fetch HTML at url. Returns empty string on failure. Retries once on 429/503 after backoff."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        if e.code in (429, 503):
            logger.warning("Got %s for %s, waiting %s s then retry once", e.code, url, BACKOFF_SEC)
            time.sleep(BACKOFF_SEC)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.read().decode("utf-8", errors="replace")
            except Exception:
                return ""
        return ""
    except Exception:
        return ""


def _extract_links(html: str, base_url: str, max_links: int = STUB_MAX_LINKS) -> list[str]:
    """Extract absolute URLs from href attributes. Dedupe, strip fragment, limit to max_links."""
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
    seen: set[str] = set()
    result: list[str] = []
    for href in hrefs:
        href = href.strip()
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        # strip fragment for dedupe
        without_fragment = parsed._replace(fragment="").geturl()
        if without_fragment in seen:
            continue
        seen.add(without_fragment)
        result.append(absolute)
        if len(result) >= max_links:
            break
    return result


def crawl_one_source(
    base_url: str = STUB_SOURCE_BASE_URL,
    source_name: str = STUB_SOURCE_NAME,
) -> list[dict]:
    """
    Fetch base_url page, extract links from body, keep only robots-allowed URLs per host.
    Returns one item per allowed link (url = link; title/body stub).
    Returns list of dicts: source, url, title, body, published_at (iso), type, metadata.
    """
    robots_txt = fetch_robots_txt(base_url)
    if not can_fetch(base_url, robots_txt):
        return []

    delay_sec = parse_crawl_delay(robots_txt)
    delay_sec = min(delay_sec if delay_sec is not None else DEFAULT_DELAY_SEC, CRAWL_DELAY_CAP_SEC)
    time.sleep(delay_sec)

    html = _fetch_page(base_url)
    if not html:
        return []

    links = _extract_links(html, base_url, max_links=STUB_MAX_LINKS)
    unique_origins = {_origin_from_url(u) for u in links}
    robots_by_origin: dict[str, str] = {}
    for origin in unique_origins:
        if not has_cached_robots(origin):
            time.sleep(min(DEFAULT_DELAY_SEC, CRAWL_DELAY_CAP_SEC))
        robots_by_origin[origin] = fetch_robots_txt(origin)

    allowed = [
        u
        for u in links
        if can_fetch(u, robots_by_origin.get(_origin_from_url(u), ""))
    ]
    if not allowed:
        return []

    return [
        {
            "source": source_name,
            "url": url,
            "title": "Stub headline for event extraction",
            "body": "Stub body. Central bank announced policy change. Market impact expected.",
            "published_at": None,
            "type": "news",
            "metadata": {"stub": True},
        }
        for url in allowed
    ]
