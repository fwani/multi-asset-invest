"""EventService: list, get by id, filters (contracts: GET /events, GET /events/{id})."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.event import Event


class EventFilters:
    """Query filters for event list (contract: type, country, from_date, to_date, limit, offset)."""

    def __init__(
        self,
        *,
        type: str | None = None,
        country: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        self.type = type
        self.country = country
        self.from_date = from_date
        self.to_date = to_date
        self.limit = min(max(1, limit), 200)
        self.offset = max(0, offset)


class EventService:
    """List events with filters, get single event by id."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self, filters: EventFilters
    ) -> tuple[list[Event], int]:
        """Return (items, total) for paginated list with filters."""
        base = select(Event)
        count_stmt = select(func.count()).select_from(Event)

        if filters.type is not None:
            base = base.where(Event.event_type == filters.type)
            count_stmt = count_stmt.where(Event.event_type == filters.type)
        if filters.country is not None:
            base = base.where(Event.country_id == filters.country)
            count_stmt = count_stmt.where(Event.country_id == filters.country)
        if filters.from_date is not None:
            base = base.where(Event.occurred_at >= filters.from_date)
            count_stmt = count_stmt.where(Event.occurred_at >= filters.from_date)
        if filters.to_date is not None:
            base = base.where(Event.occurred_at <= filters.to_date)
            count_stmt = count_stmt.where(Event.occurred_at <= filters.to_date)

        base = base.order_by(Event.occurred_at.desc())
        base = base.offset(filters.offset).limit(filters.limit)

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()
        items_result = await self._session.execute(base)
        items = list(items_result.scalars().all())
        return items, total

    async def get_by_id(self, event_id: int) -> Event | None:
        """Return event by id or None."""
        stmt = select(Event).where(Event.id == event_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_source(self, event_id: int) -> Event | None:
        """Return event by id with news (source) loaded, or None."""
        stmt = (
            select(Event)
            .where(Event.id == event_id)
            .options(selectinload(Event.news))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
