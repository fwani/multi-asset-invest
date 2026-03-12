"""Stub crawler: fetch base_url page, extract links from body, return items for robots-allowed URLs."""

import logging
import re
import time
import urllib.request
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse

from crawlers.browser_fetch import fetch_page_with_browser
from crawlers.content_extractor import extract_content
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
DEFAULT_MAX_LINKS_PER_PAGE = 20
DEFAULT_MAX_PAGES_TOTAL = 100

# Safety: plan constants
DEFAULT_DELAY_SEC = 1.0
CRAWL_DELAY_CAP_SEC = 60
BACKOFF_SEC = 60

# When filtering by article, scan up to this many raw links so we can fill the article cap.
MAX_RAW_LINKS_TO_SCAN = 200

# Only collect items with published_at within this many days (None = no filter).
DEFAULT_MAX_AGE_DAYS = 7

# Article link filter: path substrings that suggest non-article (menu, nav, static pages).
DEFAULT_BLOCK_PATTERNS = [
    "about", "contact", "login", "logout", "search", "category", "tag", "author",
    "menu", "signup", "signin", "privacy", "terms", "feed", "rss", "atom",
    "wp-login", "wp-admin", "cart", "checkout", "account", "profile", "settings",
    "subscribe", "newsletter",
]

logger = logging.getLogger(__name__)


def _origin_from_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme or 'https'}://{p.netloc}"


def _normalize_url(url: str) -> str:
    """Strip fragment for consistent dedupe; same rule as _extract_links."""
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl()


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


def _is_likely_article_url(
    url: str,
    block_patterns: list[str] | None = None,
    allow_patterns: list[str] | None = None,
) -> bool:
    """
    Return True if url looks like an article link (not menu/nav/static).
    block_patterns: path substrings to exclude (e.g. /about, /login). Uses DEFAULT_BLOCK_PATTERNS if None.
    allow_patterns: if set, path must contain at least one of these; if None, only block is applied.
    """
    parsed = urlparse(url)
    path = (parsed.path or "/").lower()
    parts = [p for p in path.split("/") if p]
    if len(parts) <= 1:
        return False
    blocks = block_patterns if block_patterns is not None else DEFAULT_BLOCK_PATTERNS
    if any(b.lower() in path for b in blocks):
        return False
    if allow_patterns is not None:
        if not any(a.lower() in path for a in allow_patterns):
            return False
    return True


def _is_recent(published_at: str | None, max_age_days: int) -> bool:
    """Return True if published_at is within the last max_age_days days (or missing)."""
    if max_age_days <= 0:
        return True
    if not published_at:
        return True
    try:
        s = published_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - dt).days
        return age_days <= max_age_days
    except (ValueError, TypeError):
        return True


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
    render_mode: str = "static",
    skip_urls: set[str] | None = None,
    max_depth: int = 2,
    max_links_per_page: int = DEFAULT_MAX_LINKS_PER_PAGE,
    max_pages_total: int = DEFAULT_MAX_PAGES_TOTAL,
    block_patterns: list[str] | None = None,
    allow_patterns: list[str] | None = None,
    max_age_days: int | None = DEFAULT_MAX_AGE_DAYS,
) -> list[dict]:
    """
    Fetch base_url page, extract links from body, keep only robots-allowed URLs per host.
    For each allowed URL (L1), fetch HTML and extract title/body/published_at.
    If max_depth >= 2, extract links (L2) from each L1 page and fetch those too.
    URLs in skip_urls (normalized) are not fetched. Total fetches capped by max_pages_total.
    If max_age_days is set, only items with published_at within that many days are returned.
    Returns list of dicts: source, url, title, body, published_at (iso), type, metadata.
    """
    skip_urls = skip_urls or set()
    seen_in_run: set[str] = set()
    pages_fetched = 0

    robots_txt = fetch_robots_txt(base_url)
    if not can_fetch(base_url, robots_txt):
        return []

    delay_sec = parse_crawl_delay(robots_txt)
    delay_sec = min(delay_sec if delay_sec is not None else DEFAULT_DELAY_SEC, CRAWL_DELAY_CAP_SEC)
    time.sleep(delay_sec)

    html = _fetch_page(base_url)
    if not html:
        return []

    raw_links = _extract_links(html, base_url, max_links=MAX_RAW_LINKS_TO_SCAN)
    seen_norm: set[str] = set()
    links: list[str] = []
    for u in raw_links:
        if not _is_likely_article_url(u, block_patterns=block_patterns, allow_patterns=allow_patterns):
            continue
        n = _normalize_url(u)
        if n in skip_urls:
            continue
        if n in seen_norm:
            continue
        seen_norm.add(n)
        links.append(u)
        if len(links) >= STUB_MAX_LINKS:
            break
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

    use_browser = (render_mode or "static").lower() == "browser"
    items: list[dict] = []
    last_origin: str | None = None
    L2_queue: list[str] = []

    for url in allowed:
        normalized = _normalize_url(url)
        if normalized in skip_urls:
            continue
        if pages_fetched >= max_pages_total:
            break
        origin = _origin_from_url(url)
        if last_origin == origin:
            time.sleep(min(DEFAULT_DELAY_SEC, CRAWL_DELAY_CAP_SEC))
        last_origin = origin

        html = fetch_page_with_browser(url) if use_browser else _fetch_page(url)
        if not html:
            continue
        seen_in_run.add(normalized)
        pages_fetched += 1
        extracted = extract_content(html)
        if max_age_days is None or _is_recent(extracted.get("published_at"), max_age_days):
            items.append({
                "source": source_name,
                "url": url,
                "title": extracted.get("title") or "",
                "body": extracted.get("body") or "",
                "published_at": extracted.get("published_at"),
                "type": "news",
                "metadata": {},
            })
        if max_depth >= 2 and html:
            raw_l2 = _extract_links(html, url, max_links=MAX_RAW_LINKS_TO_SCAN)
            l2_added = 0
            for l2_url in raw_l2:
                if l2_added >= max_links_per_page:
                    break
                if not _is_likely_article_url(l2_url, block_patterns=block_patterns, allow_patterns=allow_patterns):
                    continue
                l2_norm = _normalize_url(l2_url)
                if l2_norm in skip_urls or l2_norm in seen_in_run:
                    continue
                seen_in_run.add(l2_norm)
                L2_queue.append(l2_url)
                l2_added += 1

    if not L2_queue or pages_fetched >= max_pages_total:
        return items

    L2_origins = {_origin_from_url(u) for u in L2_queue}
    for origin in L2_origins:
        if origin not in robots_by_origin:
            if not has_cached_robots(origin):
                time.sleep(min(DEFAULT_DELAY_SEC, CRAWL_DELAY_CAP_SEC))
            robots_by_origin[origin] = fetch_robots_txt(origin)

    allowed_L2 = [
        u
        for u in L2_queue
        if can_fetch(u, robots_by_origin.get(_origin_from_url(u), ""))
    ]
    last_origin = None
    for url in allowed_L2:
        normalized = _normalize_url(url)
        if normalized in skip_urls:
            continue
        if pages_fetched >= max_pages_total:
            break
        origin = _origin_from_url(url)
        if last_origin == origin:
            time.sleep(min(DEFAULT_DELAY_SEC, CRAWL_DELAY_CAP_SEC))
        last_origin = origin

        html = fetch_page_with_browser(url) if use_browser else _fetch_page(url)
        if not html:
            continue
        pages_fetched += 1
        extracted = extract_content(html)
        if max_age_days is None or _is_recent(extracted.get("published_at"), max_age_days):
            items.append({
                "source": source_name,
                "url": url,
                "title": extracted.get("title") or "",
                "body": extracted.get("body") or "",
                "published_at": extracted.get("published_at"),
                "type": "news",
                "metadata": {},
            })

    return items
