"""Event API: GET /events, GET /events/{id} (contracts/api.md)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from models.event import Event
from services.event_service import EventFilters, EventService


router = APIRouter()


class EventListItem(BaseModel):
    id: int
    event_type: str
    country_id: int | None
    actor: str | None
    impact_type: str | None
    occurred_at: datetime
    source_summary: str | None
    confidence: float | None
    extracted_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    items: list[EventListItem]
    total: int


class NewsSource(BaseModel):
    id: int
    source: str
    url: str | None
    title: str | None

    model_config = {"from_attributes": True}


class EventDetailResponse(BaseModel):
    id: int
    event_type: str
    country_id: int | None
    actor: str | None
    impact_type: str | None
    occurred_at: datetime
    source_summary: str | None
    confidence: float | None
    extracted_at: datetime
    source: NewsSource | None = None
    metadata_: dict | None = None

    model_config = {"from_attributes": True}


def _event_to_detail(event: Event) -> dict:
    data: dict = {
        "id": event.id,
        "event_type": event.event_type,
        "country_id": event.country_id,
        "actor": event.actor,
        "impact_type": event.impact_type,
        "occurred_at": event.occurred_at,
        "source_summary": event.source_summary,
        "confidence": event.confidence,
        "extracted_at": event.extracted_at,
        "metadata_": event.metadata_,
    }
    if event.news is not None:
        data["source"] = NewsSource(
            id=event.news.id,
            source=event.news.source,
            url=event.news.url,
            title=event.news.title,
        )
    else:
        data["source"] = None
    return data


@router.get("", response_model=EventListResponse)
async def list_events(
    type: str | None = Query(None, alias="type", description="event_type filter"),
    country: int | None = Query(None, description="country_id filter"),
    from_date: datetime | None = Query(None, description="occurred_at from"),
    to_date: datetime | None = Query(None, description="occurred_at to"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    """List events with optional filters (type, country, from_date, to_date, limit, offset)."""
    filters = EventFilters(
        type=type,
        country=country,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    svc = EventService(session)
    items, total = await svc.list(filters)
    return EventListResponse(
        items=[EventListItem.model_validate(e) for e in items],
        total=total,
    )


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Get single event by id; includes source (news) and extracted attributes."""
    svc = EventService(session)
    event = await svc.get_by_id_with_source(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return EventDetailResponse(**_event_to_detail(event))