"""Aggregate API router. Mount at root in main; prefix /api/v1 applied here."""

from fastapi import APIRouter

from api import crawl_sources, events, health, impacts, worker

api_router = APIRouter(prefix="/api/v1", tags=["api"])
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(impacts.router, prefix="", tags=["impacts"])
api_router.include_router(worker.router, prefix="", tags=["worker"])
api_router.include_router(crawl_sources.router, prefix="", tags=["crawl-sources"])
