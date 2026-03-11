"""Worker trigger API: enqueue crawl/pipeline jobs to Redis (수동 크롤·파이프라인 트리거)."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from redis.asyncio import Redis

from core.redis import get_redis

# Queue key must match worker's core.redis_client.QUEUE_JOBS
QUEUE_JOBS = "multi_asset_invest:queue:jobs"

router = APIRouter()


class WorkerTriggerRequest(BaseModel):
    """Request body for triggering a worker job."""

    job_type: str = "crawl_and_extract"
    event_id: int | None = None


class WorkerTriggerResponse(BaseModel):
    """Response after enqueueing a job."""

    ok: bool = True
    job_type: str
    message: str


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
) -> WorkerTriggerResponse:
    job_type = (body or WorkerTriggerRequest()).job_type
    event_id = (body or WorkerTriggerRequest()).event_id

    if job_type == "crawl_and_extract":
        payload = {"type": "crawl_and_extract"}
    elif job_type == "event_created":
        if event_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="event_id required for job_type=event_created",
            )
        payload = {"type": "event_created", "event_id": event_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown job_type: {job_type}. Use crawl_and_extract or event_created.",
        )

    raw = json.dumps(payload)
    await redis.lpush(QUEUE_JOBS, raw)

    return WorkerTriggerResponse(
        job_type=job_type,
        message="Job enqueued",
    )
