"""CrawlSource model (FR-002-2): admin-configured data collection sources."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.models.base import Base


class CrawlSource(Base):
    __tablename__ = "crawl_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    base_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    render_mode: Mapped[str] = mapped_column(String(32), nullable=False, server_default="static")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
