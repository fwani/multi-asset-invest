"""Pipeline: crawl → save News → extract → save Event, enqueue via Redis."""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from multiprocessing import Queue

from sqlalchemy import select

from core.database import async_session_factory
from core.redis_client import QUEUE_JOBS, get_redis
from crawlers.stub_crawler import _normalize_url, crawl_one_source
from models.country import Country  # noqa: F401 — ensure countries table in metadata for Event FK
from models.crawl_source import CrawlSource
from models.event import Event
from models.news import News
from pipelines.crawl_queue import CrawlResult, CrawlTask, collect_crawl_results
from pipelines.event_extractor import extract_events

logger = logging.getLogger(__name__)


async def _get_active_crawl_sources() -> list[tuple[str, str, str]]:
    """(base_url, source_name, render_mode) for is_active=True. Same DB as API."""
    async with async_session_factory() as session:
        stmt = select(
            CrawlSource.base_url,
            CrawlSource.source_name,
            CrawlSource.render_mode,
        ).where(CrawlSource.is_active.is_(True))
        result = await session.execute(stmt)
        return [(row[0], row[1], row[2] or "static") for row in result.all()]


async def _get_seen_urls_from_db(days: int = 30) -> set[str]:
    """Return normalized URLs already stored in News (recent N days) to avoid re-requesting."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    async with async_session_factory() as session:
        stmt = select(News.url).where(
            News.url.isnot(None),
            News.created_at >= cutoff,
        )
        result = await session.execute(stmt)
        return {_normalize_url(row[0]) for row in result.all() if row[0]}


async def run_crawl_and_extract(in_queue: Queue, out_queue: Queue) -> None:
    """
    Crawl sources via worker processes: put one CrawlTask per active source,
    collect CrawlResults, merge and dedupe by URL, then save News/Event and enqueue.
    When no active sources, run stub crawl in-process.
    """
    active = await _get_active_crawl_sources()
    if active:
        db_seen = await _get_seen_urls_from_db()
        for base_url, source_name, render_mode in active:
            in_queue.put(
                CrawlTask(
                    base_url=base_url,
                    source_name=source_name,
                    render_mode=render_mode or "static",
                    skip_urls=db_seen,
                )
            )
        loop = asyncio.get_event_loop()
        results: list[CrawlResult] = await loop.run_in_executor(
            None,
            collect_crawl_results,
            out_queue,
            len(active),
        )
        raw_items = []
        seen_url: set[str] = set()
        for r in results:
            for item in r.items:
                url = item.get("url")
                if url:
                    norm = _normalize_url(url)
                    if norm in seen_url:
                        continue
                    seen_url.add(norm)
                raw_items.append(item)
    else:
        raw_items = crawl_one_source()

    if not raw_items:
        logger.info("Crawl returned no items")
        return

    async with async_session_factory() as session:
        # Country code -> id cache for event country_id resolution
        r = await session.execute(select(Country.id, Country.code))
        country_code_to_id: dict[str, int] = {row[1]: row[0] for row in r.all() if row[1]}

        event_objects: list[Event] = []
        for raw in raw_items:
            body = raw.get("body") or raw.get("title") or ""
            published_at = raw.get("published_at")
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(
                        published_at.replace("Z", "+00:00")
                    )
                except ValueError:
                    published_at = None
            if published_at is None:
                published_at = datetime.now(timezone.utc)

            news = News(
                source=raw.get("source", "unknown"),
                url=raw.get("url"),
                title=raw.get("title"),
                body=body,
                published_at=published_at if raw.get("published_at") else None,
                type=raw.get("type"),
                metadata_=raw.get("metadata"),
            )
            session.add(news)
            await session.flush()

            for attrs in extract_events(body, occurred_at=published_at):
                country_id = attrs.get("country_id")
                if country_id is None and attrs.get("country_code"):
                    country_id = country_code_to_id.get(
                        (attrs.get("country_code") or "").strip().upper()
                    )
                event = Event(
                    news_id=news.id,
                    event_type=attrs.get("event_type", "unknown"),
                    country_id=country_id,
                    actor=attrs.get("actor"),
                    impact_type=attrs.get("impact_type"),
                    occurred_at=attrs["occurred_at"],
                    source_summary=attrs.get("source_summary"),
                    confidence=attrs.get("confidence"),
                    metadata_=attrs.get("metadata_"),
                )
                session.add(event)
                await session.flush()
                event_objects.append(event)

        await session.commit()

    redis = get_redis()
    try:
        for event in event_objects:
            payload = json.dumps({"type": "event_created", "event_id": event.id})
            await redis.lpush(QUEUE_JOBS, payload)
            logger.info("Enqueued event_created event_id=%s", event.id)
    finally:
        await redis.aclose()
