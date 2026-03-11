"""Async DB engine and session for worker (shared DB with API)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    """Create a new async session (use in pipeline steps)."""
    return async_session_factory()


async def check_connection() -> bool:
    """Verify DB connection."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True
