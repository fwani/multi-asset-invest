"""Assets API: GET /assets, GET /assets/{id} (contracts/api.md FR-018)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.asset_service import AssetFilters, AssetService

router = APIRouter()


class AssetListItem(BaseModel):
    id: int
    symbol: str
    name: str
    asset_type: str
    currency_id: int | None
    exchange: str | None
    sector_id: int | None
    country_id: int | None

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    items: list[AssetListItem]
    total: int


class AssetDetailResponse(BaseModel):
    id: int
    symbol: str
    name: str
    asset_type: str
    currency_id: int | None
    exchange: str | None
    sector_id: int | None
    country_id: int | None

    model_config = {"from_attributes": True}


class AssetCreateBody(BaseModel):
    symbol: str
    name: str
    asset_type: str
    currency_id: int | None = None
    exchange: str | None = None
    sector_id: int | None = None
    country_id: int | None = None


@router.get("", response_model=AssetListResponse)
async def list_assets(
    asset_type: str | None = Query(None, description="Filter by asset_type (FR-018)"),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_async_session),
):
    """List supported assets (FR-018: stock, crypto, fx, bond, gold, commodity)."""
    filters = AssetFilters(asset_type=asset_type, limit=limit)
    svc = AssetService(session)
    items, total = await svc.list(filters)
    return AssetListResponse(
        items=[AssetListItem.model_validate(a) for a in items],
        total=total,
    )


@router.get("/{asset_id}", response_model=AssetDetailResponse)
async def get_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Get single asset by id."""
    svc = AssetService(session)
    asset = await svc.get_by_id(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    return AssetDetailResponse.model_validate(asset)


@router.post("", response_model=AssetDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    body: AssetCreateBody,
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new asset (symbol, name, asset_type required; FR-018)."""
    svc = AssetService(session)
    try:
        asset = await svc.create(
            symbol=body.symbol,
            name=body.name,
            asset_type=body.asset_type,
            currency_id=body.currency_id,
            exchange=body.exchange,
            sector_id=body.sector_id,
            country_id=body.country_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Asset with this symbol already exists",
        )
    await session.commit()
    return AssetDetailResponse.model_validate(asset)
