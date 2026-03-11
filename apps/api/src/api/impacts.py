"""Impacts API: GET /events/{event_id}/impacts, GET /assets/{asset_id}/impacts (contracts/api.md)."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.asset_impact_service import AssetImpactFilters, AssetImpactService

router = APIRouter()


class AssetImpactResponse(BaseModel):
    id: int
    event_id: int
    asset_id: int
    direction: str
    strength: float | None
    computed_at: datetime

    model_config = {"from_attributes": True}


@router.get("/events/{event_id}/impacts", response_model=list[AssetImpactResponse])
async def list_impacts_by_event(
    event_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Return asset impacts for the given event."""
    svc = AssetImpactService(session)
    items = await svc.list_by_event_id(event_id)
    return [AssetImpactResponse.model_validate(i) for i in items]


@router.get("/assets/{asset_id}/impacts", response_model=list[AssetImpactResponse])
async def list_impacts_by_asset(
    asset_id: int,
    from_date: datetime | None = Query(None, description="computed_at from"),
    to_date: datetime | None = Query(None, description="computed_at to"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
):
    """Return impacts for the given asset (optional from_date, to_date, limit)."""
    filters = AssetImpactFilters(from_date=from_date, to_date=to_date, limit=limit)
    svc = AssetImpactService(session)
    items = await svc.list_by_asset_id(asset_id, filters)
    return [AssetImpactResponse.model_validate(i) for i in items]
