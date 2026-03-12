"""Extract title, body, published_at from HTML (bs4). Used for both static and browser-rendered HTML."""

from datetime import datetime, timezone

from bs4 import BeautifulSoup

BODY_MAX_LENGTH = 50_000


def extract_content(html: str) -> dict[str, str | None]:
    """
    Parse HTML and return dict with title, body, published_at (iso string or None).
    Body is plain text from article/main/[role=main]/body; length capped at BODY_MAX_LENGTH.
    """
    if not html or not html.strip():
        return {"title": "", "body": "", "published_at": None}

    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup.find_all(["script", "style", "nav", "footer"]):
        tag.decompose()

    title = _extract_title(soup)
    body = _extract_body(soup)
    published_at = _extract_published_at(soup)

    return {"title": title, "body": body, "published_at": published_at}


def _extract_title(soup: BeautifulSoup) -> str:
    tag = soup.find("title")
    if tag and tag.get_text(strip=True):
        return tag.get_text(separator=" ", strip=True)
    meta = soup.find("meta", attrs={"property": "og:title"}) or soup.find(
        "meta", attrs={"name": "twitter:title"}
    )
    if meta and meta.get("content"):
        return meta["content"].strip()
    return ""


def _extract_body(soup: BeautifulSoup) -> str:
    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"role": "main"})
        or soup.find("body")
    )
    if not container:
        return ""
    text = container.get_text(separator=" ", strip=True)
    if len(text) > BODY_MAX_LENGTH:
        text = text[:BODY_MAX_LENGTH]
    return text


def _extract_published_at(soup: BeautifulSoup) -> str | None:
    # article:published_time
    meta = soup.find("meta", attrs={"property": "article:published_time"})
    if meta and meta.get("content"):
        s = meta["content"].strip()
        parsed = _parse_iso_or_date(s)
        if parsed:
            return parsed

    # time datetime
    time_tag = soup.find("time", attrs={"datetime": True})
    if time_tag and time_tag.get("datetime"):
        s = time_tag["datetime"].strip()
        parsed = _parse_iso_or_date(s)
        if parsed:
            return parsed

    # itemprop="datePublished"
    tag = soup.find(attrs={"itemprop": "datePublished"})
    if tag:
        dt = tag.get("datetime") or (tag.get_text(strip=True) if tag else None)
        if dt:
            parsed = _parse_iso_or_date(dt.strip())
            if parsed:
                return parsed

    return None


def _parse_iso_or_date(s: str) -> str | None:
    """Try to parse date string and return ISO format; on failure return None."""
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            continue
    return None
