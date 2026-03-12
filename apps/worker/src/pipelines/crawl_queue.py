"""Crawl queue: main puts CrawlTask; workers run crawl_one_source and put CrawlResult."""

import logging
from dataclasses import dataclass
from multiprocessing import Process, Queue

logger = logging.getLogger(__name__)


class _Poison:
    """Sentinel for worker shutdown. Put one per worker so each worker exits."""


POISON_PILL = _Poison()


@dataclass
class CrawlTask:
    """One crawl job: one source. Must be picklable (no DB/Redis)."""
    base_url: str
    source_name: str
    render_mode: str
    skip_urls: set[str]


@dataclass
class CrawlResult:
    """Result from one source. error set on exception."""
    source_name: str
    items: list[dict]
    error: str | None = None


def run_worker(in_queue: Queue, out_queue: Queue) -> None:
    """
    Run in a child process: get CrawlTask from in_queue, call crawl_one_source, put CrawlResult.
    Exit on POISON_PILL or get timeout (allows shutdown polling).
    """
    import crawlers.browser_fetch as browser_fetch  # avoid top-level import for process

    while True:
        try:
            task = in_queue.get(timeout=1.0)
        except Exception:
            continue
        if task is POISON_PILL or isinstance(task, _Poison):
            try:
                browser_fetch.close_browser()
            except Exception:
                pass
            break
        if not isinstance(task, CrawlTask):
            logger.warning("Unexpected task type: %s", type(task))
            continue
        try:
            from crawlers.stub_crawler import crawl_one_source

            items = crawl_one_source(
                base_url=task.base_url,
                source_name=task.source_name,
                render_mode=task.render_mode or "static",
                skip_urls=task.skip_urls or set(),
            )
            out_queue.put(CrawlResult(source_name=task.source_name, items=items, error=None))
        except Exception as e:
            logger.exception("Crawl failed for %s: %s", task.source_name, e)
            out_queue.put(CrawlResult(source_name=task.source_name, items=[], error=str(e)))


def start_crawl_workers(n: int, in_queue: Queue, out_queue: Queue) -> list[Process]:
    """Start n worker processes. Returns list of Process for join/terminate."""
    procs: list[Process] = []
    for i in range(n):
        p = Process(target=run_worker, args=(in_queue, out_queue), name=f"crawl-worker-{i}")
        p.start()
        procs.append(p)
    logger.info("Started %d crawl worker processes", n)
    return procs


def collect_crawl_results(
    out_queue: Queue,
    num_sources: int,
    timeout_per_result: float = 600.0,
) -> list[CrawlResult]:
    """
    Block until num_sources CrawlResult items are read from out_queue.
    Each get uses timeout_per_result. Returns list of CrawlResult (may include errors).
    """
    results: list[CrawlResult] = []
    for _ in range(num_sources):
        try:
            r = out_queue.get(timeout=timeout_per_result)
        except Exception as e:
            logger.warning("Timed out or error waiting for crawl result: %s", e)
            continue
        if isinstance(r, CrawlResult):
            results.append(r)
    return results
