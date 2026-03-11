"""Seed minimal Country, Currency, Sector, Asset. Run: cd apps/api && PYTHONPATH=src uv run python -m scripts.seed"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_factory
from models import Asset, Country, Currency, Sector


async def seed(session: AsyncSession) -> None:
    """Insert minimal master data if not present."""
    # Countries
    r = await session.execute(select(Country).limit(1))
    if r.scalar_one_or_none() is None:
        session.add_all([
            Country(code="KR", name="South Korea", type="country"),
            Country(code="US", name="United States", type="country"),
            Country(code="JP", name="Japan", type="country"),
        ])
        await session.flush()

    # Currencies
    r = await session.execute(select(Currency).limit(1))
    if r.scalar_one_or_none() is None:
        session.add_all([
            Currency(code="KRW", name="Korean Won", type="fiat"),
            Currency(code="USD", name="US Dollar", type="fiat"),
            Currency(code="JPY", name="Japanese Yen", type="fiat"),
        ])
        await session.flush()

    # Sectors
    r = await session.execute(select(Sector).limit(1))
    if r.scalar_one_or_none() is None:
        session.add_all([
            Sector(code="tech", name="Technology", type="sector"),
            Sector(code="finance", name="Finance", type="sector"),
            Sector(code="energy", name="Energy", type="sector"),
        ])
        await session.flush()

    # Minimal assets (need currency_id, sector_id, country_id from above)
    r = await session.execute(select(Asset).limit(1))
    if r.scalar_one_or_none() is None:
        currencies = (await session.execute(select(Currency))).scalars().all()
        sectors = (await session.execute(select(Sector))).scalars().all()
        countries = (await session.execute(select(Country))).scalars().all()
        c_usd = next((c for c in currencies if c.code == "USD"), None)
        c_krw = next((c for c in currencies if c.code == "KRW"), None)
        s_tech = next((s for s in sectors if s.code == "tech"), None)
        cnt_us = next((c for c in countries if c.code == "US"), None)
        cnt_kr = next((c for c in countries if c.code == "KR"), None)
        session.add_all([
            Asset(
                symbol="SPY",
                name="SPDR S&P 500 ETF",
                asset_type="stock",
                currency_id=c_usd.id if c_usd else None,
                exchange="NYSE",
                sector_id=s_tech.id if s_tech else None,
                country_id=cnt_us.id if cnt_us else None,
            ),
            Asset(
                symbol="BTCKRW",
                name="Bitcoin/KRW",
                asset_type="crypto",
                currency_id=c_krw.id if c_krw else None,
                exchange="local",
                sector_id=None,
                country_id=cnt_kr.id if cnt_kr else None,
            ),
        ])
    await session.commit()


async def main() -> None:
    async with async_session_factory() as session:
        await seed(session)
    print("Seed done.")


if __name__ == "__main__":
    asyncio.run(main())
