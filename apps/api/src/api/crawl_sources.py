"""Crawl sources API: GET/POST/PATCH/DELETE /crawl-sources (FR-002-2)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.crawl_source_service import CrawlSourceService

router = APIRouter()


class CrawlSourceItem(BaseModel):
    id: int
    base_url: str
    source_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CrawlSourceListResponse(BaseModel):
    items: list[CrawlSourceItem]
    total: int


class CrawlSourceCreate(BaseModel):
    base_url: str
    source_name: str
    is_active: bool = True


class CrawlSourceUpdate(BaseModel):
    base_url: str | None = None
    source_name: str | None = None
    is_active: bool | None = None


@router.get("/crawl-sources", response_model=CrawlSourceListResponse)
async def list_crawl_sources(
    is_active: bool | None = Query(None, description="Filter by active"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    svc = CrawlSourceService(session)
    items, total = await svc.list(is_active=is_active, limit=limit, offset=offset)
    return CrawlSourceListResponse(items=[CrawlSourceItem.model_validate(x) for x in items], total=total)


@router.get("/crawl-sources/{id}", response_model=CrawlSourceItem)
async def get_crawl_source(
    id: int,
    session: AsyncSession = Depends(get_async_session),
):
    svc = CrawlSourceService(session)
    row = await svc.get(id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl source not found")
    return CrawlSourceItem.model_validate(row)


@router.post("/crawl-sources", response_model=CrawlSourceItem, status_code=status.HTTP_201_CREATED)
async def create_crawl_source(
    body: CrawlSourceCreate,
    session: AsyncSession = Depends(get_async_session),
):
    svc = CrawlSourceService(session)
    row = await svc.create(
        base_url=body.base_url,
        source_name=body.source_name,
        is_active=body.is_active,
    )
    await session.commit()
    return CrawlSourceItem.model_validate(row)


@router.patch("/crawl-sources/{id}", response_model=CrawlSourceItem)
async def update_crawl_source(
    id: int,
    body: CrawlSourceUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    svc = CrawlSourceService(session)
    row = await svc.update(
        id,
        base_url=body.base_url,
        source_name=body.source_name,
        is_active=body.is_active,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl source not found")
    await session.commit()
    return CrawlSourceItem.model_validate(row)


@router.delete("/crawl-sources/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crawl_source(
    id: int,
    session: AsyncSession = Depends(get_async_session),
):
    svc = CrawlSourceService(session)
    ok = await svc.delete(id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl source not found")
    await session.commit()
