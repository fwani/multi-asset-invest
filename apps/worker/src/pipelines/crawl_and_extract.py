"""Pipeline: crawl → save News → extract → save Event, enqueue via Redis."""

import asyncio
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from core.database import async_session_factory
from core.redis_client import QUEUE_JOBS, get_redis
from crawlers.stub_crawler import crawl_one_source
from models.country import Country  # noqa: F401 — ensure countries table in metadata for Event FK
from models.crawl_source import CrawlSource
from models.event import Event
from models.news import News
from pipelines.event_extractor import extract_events

logger = logging.getLogger(__name__)


async def _get_active_crawl_sources() -> list[tuple[str, str]]:
    """Return list of (base_url, source_name) for is_active=True. Uses same DB as API."""
    async with async_session_factory() as session:
        stmt = select(CrawlSource.base_url, CrawlSource.source_name).where(
            CrawlSource.is_active.is_(True)
        )
        result = await session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]


async def run_crawl_and_extract() -> None:
    """
    Crawl sources (from DB if any active CrawlSource, else stub), save News rows,
    extract events, save Event rows, then enqueue each new event_id to Redis.
    """
    active = await _get_active_crawl_sources()
    if active:
        raw_items = []
        for i, (base_url, source_name) in enumerate(active):
            if i > 0:
                await asyncio.sleep(1.0)
            items = crawl_one_source(base_url=base_url, source_name=source_name)
            raw_items.extend(items)
    else:
        raw_items = crawl_one_source()

    if not raw_items:
        logger.info("Crawl returned no items")
        return

    async with async_session_factory() as session:
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
                event = Event(
                    news_id=news.id,
                    event_type=attrs.get("event_type", "unknown"),
                    country_id=attrs.get("country_id"),
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
