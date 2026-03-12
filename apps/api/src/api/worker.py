"""Worker trigger API: enqueue crawl/pipeline jobs to Redis (수동 크롤·파이프라인 트리거)."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.redis import get_redis
from services.event_service import EventFilters, EventService

# Queue key must match worker's core.redis_client.QUEUE_JOBS
QUEUE_JOBS = "multi_asset_invest:queue:jobs"

router = APIRouter()

RECALC_IMPACTS_LIMIT_DEFAULT = 200
RECALC_IMPACTS_LIMIT_MAX = 500


class WorkerTriggerRequest(BaseModel):
    """Request body for triggering a worker job."""

    job_type: str = "crawl_and_extract"
    event_id: int | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    limit: int | None = None


class WorkerTriggerResponse(BaseModel):
    """Response after enqueueing a job."""

    ok: bool = True
    job_type: str
    message: str
    enqueued_count: int | None = None


@router.post(
    "/worker/trigger",
    response_model=WorkerTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger worker job",
    description="Enqueue a crawl or pipeline job to Redis for the worker to process.",
)
async def post_worker_trigger(
    body: WorkerTriggerRequest | None = None,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_async_session),
) -> WorkerTriggerResponse:
    req = body or WorkerTriggerRequest()
    job_type = req.job_type
    event_id = req.event_id

    if job_type == "crawl_and_extract":
        payload = {"type": "crawl_and_extract"}
        raw = json.dumps(payload)
        await redis.lpush(QUEUE_JOBS, raw)
        return WorkerTriggerResponse(job_type=job_type, message="Job enqueued")
    if job_type == "event_created":
        if event_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="event_id required for job_type=event_created",
            )
        payload = {"type": "event_created", "event_id": event_id}
        raw = json.dumps(payload)
        await redis.lpush(QUEUE_JOBS, raw)
        return WorkerTriggerResponse(job_type=job_type, message="Job enqueued")
    if job_type == "recalc_impacts":
        limit = req.limit if req.limit is not None else RECALC_IMPACTS_LIMIT_DEFAULT
        limit = min(max(1, limit), RECALC_IMPACTS_LIMIT_MAX)
        filters = EventFilters(
            from_date=req.from_date,
            to_date=req.to_date,
            limit=limit,
            offset=0,
        )
        svc = EventService(session)
        events_list, _ = await svc.list(filters)
        enqueued = 0
        for ev in events_list:
            raw = json.dumps({"type": "event_created", "event_id": ev.id})
            await redis.lpush(QUEUE_JOBS, raw)
            enqueued += 1
        return WorkerTriggerResponse(
            job_type=job_type,
            message="Recalc impacts enqueued",
            enqueued_count=enqueued,
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown job_type: {job_type}. Use crawl_and_extract, event_created, or recalc_impacts.",
    )
