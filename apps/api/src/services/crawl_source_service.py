"""CrawlSourceService: list, get, create, update, delete (FR-002-2)."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.crawl_source import CrawlSource


class CrawlSourceService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self,
        *,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[CrawlSource], int]:
        base = select(CrawlSource)
        count_stmt = select(func.count()).select_from(CrawlSource)
        if is_active is not None:
            base = base.where(CrawlSource.is_active == is_active)
            count_stmt = count_stmt.where(CrawlSource.is_active == is_active)
        limit = min(max(1, limit), 200)
        offset = max(0, offset)
        total = (await self._session.execute(count_stmt)).scalar_one()
        base = base.order_by(CrawlSource.id).limit(limit).offset(offset)
        result = await self._session.execute(base)
        items = list(result.scalars().all())
        return items, total

    async def get(self, id: int) -> CrawlSource | None:
        stmt = select(CrawlSource).where(CrawlSource.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        base_url: str,
        source_name: str,
        is_active: bool = True,
        render_mode: str = "static",
    ) -> CrawlSource:
        row = CrawlSource(
            base_url=base_url,
            source_name=source_name,
            is_active=is_active,
            render_mode=render_mode,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def update(
        self,
        id: int,
        *,
        base_url: str | None = None,
        source_name: str | None = None,
        is_active: bool | None = None,
        render_mode: str | None = None,
    ) -> CrawlSource | None:
        row = await self.get(id)
        if row is None:
            return None
        if base_url is not None:
            row.base_url = base_url
        if source_name is not None:
            row.source_name = source_name
        if is_active is not None:
            row.is_active = is_active
        if render_mode is not None:
            row.render_mode = render_mode
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def delete(self, id: int) -> bool:
        row = await self.get(id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True
