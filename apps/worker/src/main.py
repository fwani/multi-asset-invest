"""Worker entry: Redis queue consumer and DB bootstrap."""

import asyncio
import json
import logging
from multiprocessing import Process, Queue

from config import settings
from core.database import check_connection, engine
from core.redis_client import QUEUE_JOBS, get_redis
from pipelines.crawl_queue import POISON_PILL, start_crawl_workers

_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(level=_level)
logger = logging.getLogger(__name__)


async def process_job(
    payload: str,
    crawl_in_queue: Queue | None,
    crawl_out_queue: Queue | None,
) -> None:
    """Process one job from queue. Supports type: crawl_and_extract, event_created (no-op stub)."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logger.warning("Invalid job payload (not JSON): %s", payload[:200])
        return
    job_type = data.get("type")
    if job_type == "crawl_and_extract":
        from pipelines.crawl_and_extract import run_crawl_and_extract
        if crawl_in_queue is not None and crawl_out_queue is not None:
            await run_crawl_and_extract(crawl_in_queue, crawl_out_queue)
        else:
            logger.warning("Crawl queues not available, skipping crawl_and_extract")
    elif job_type == "event_created":
        from pipelines.impact_calculator import run_impact_calculation
        event_id = data.get("event_id")
        if event_id is not None:
            await run_impact_calculation(int(event_id))
        else:
            logger.warning("event_created job missing event_id")
    else:
        logger.info("Job received: type=%s", job_type)


async def run_consumer() -> None:
    """Bootstrap DB, start crawl workers, then consume from Redis queue."""
    try:
        await check_connection()
        logger.info("DB connection OK")
    except Exception as e:
        logger.error("DB connection failed: %s", e)
        raise

    crawl_in_queue: Queue | None = None
    crawl_out_queue: Queue | None = None
    crawl_workers: list[Process] = []

    n = max(1, getattr(settings, "crawl_worker_count", 2))
    crawl_in_queue = Queue()
    crawl_out_queue = Queue()
    crawl_workers = start_crawl_workers(n, crawl_in_queue, crawl_out_queue)

    redis = get_redis()
    try:
        while True:
            # Block until a job is available (timeout 5s to allow graceful shutdown)
            result = await redis.brpop(QUEUE_JOBS, timeout=5)
            if result is None:
                continue
            _key, payload = result
            await process_job(payload, crawl_in_queue, crawl_out_queue)
    finally:
        for _ in crawl_workers:
            crawl_in_queue.put(POISON_PILL)
        for w in crawl_workers:
            w.join(timeout=5)
            if w.is_alive():
                w.terminate()
        await redis.aclose()
        await engine.dispose()


def main() -> None:
    asyncio.run(run_consumer())


if __name__ == "__main__":
    main()
