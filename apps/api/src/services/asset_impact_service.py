"""AssetImpactService: list by event_id, list by asset_id (contracts: GET events/{id}/impacts, GET assets/{id}/impacts)."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.asset_impact import AssetImpact


class AssetImpactFilters:
    """Filters for asset impacts (asset list: from_date, to_date, limit)."""

    def __init__(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
    ):
        self.from_date = from_date
        self.to_date = to_date
        self.limit = min(max(1, limit), 200)


class AssetImpactService:
    """List impacts by event_id or by asset_id with optional date range."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_by_event_id(
        self,
        event_id: int,
    ) -> list[AssetImpact]:
        """Return impacts for the given event (for GET /events/{id}/impacts)."""
        stmt = (
            select(AssetImpact)
            .where(AssetImpact.event_id == event_id)
            .options(
                selectinload(AssetImpact.event),
                selectinload(AssetImpact.asset),
            )
            .order_by(AssetImpact.computed_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_asset_id(
        self,
        asset_id: int,
        filters: AssetImpactFilters,
    ) -> list[AssetImpact]:
        """Return impacts for the given asset (for GET /assets/{id}/impacts)."""
        stmt = (
            select(AssetImpact)
            .where(AssetImpact.asset_id == asset_id)
        )
        if filters.from_date is not None:
            stmt = stmt.where(AssetImpact.computed_at >= filters.from_date)
        if filters.to_date is not None:
            stmt = stmt.where(AssetImpact.computed_at <= filters.to_date)
        stmt = (
            stmt.options(
                selectinload(AssetImpact.event),
                selectinload(AssetImpact.asset),
            )
            .order_by(AssetImpact.computed_at.desc())
            .limit(filters.limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
