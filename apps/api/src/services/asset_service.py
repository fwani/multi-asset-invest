"""AssetService: list (asset_type, limit), get by id (contracts: GET /assets, GET /assets/{id}, FR-018)."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset


class AssetFilters:
    """Filters for asset list (contract: asset_type, limit)."""

    def __init__(
        self,
        *,
        asset_type: str | None = None,
        limit: int = 100,
    ):
        self.asset_type = asset_type
        self.limit = min(max(1, limit), 500)


class AssetService:
    """List assets with optional asset_type filter; get single asset by id."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self, filters: AssetFilters) -> tuple[list[Asset], int]:
        """Return (items, total) for asset list (FR-018 supported asset types)."""
        base = select(Asset)
        count_stmt = select(func.count()).select_from(Asset)
        if filters.asset_type is not None:
            base = base.where(Asset.asset_type == filters.asset_type)
            count_stmt = count_stmt.where(Asset.asset_type == filters.asset_type)
        base = base.order_by(Asset.symbol.asc()).limit(filters.limit)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()
        items_result = await self._session.execute(base)
        items = list(items_result.scalars().all())
        return items, total

    async def get_by_id(self, asset_id: int) -> Asset | None:
        """Return asset by id or None."""
        stmt = select(Asset).where(Asset.id == asset_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        symbol: str,
        name: str,
        asset_type: str,
        currency_id: int | None = None,
        exchange: str | None = None,
        sector_id: int | None = None,
        country_id: int | None = None,
    ) -> Asset:
        """Create a new asset (FR-018 supported types)."""
        row = Asset(
            symbol=symbol.strip(),
            name=name.strip(),
            asset_type=asset_type.strip(),
            currency_id=currency_id,
            exchange=exchange.strip() if exchange else None,
            sector_id=sector_id,
            country_id=country_id,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row
