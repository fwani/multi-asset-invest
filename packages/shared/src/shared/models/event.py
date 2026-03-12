"""Event model (extracted market event from news)."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base

# Import after Signal is defined (event_signals table)
from shared.models.signal import event_signals


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    news_id: Mapped[int | None] = mapped_column(
        ForeignKey("news.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"), nullable=True
    )
    actor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    impact_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    news = relationship("News", back_populates="events")
    country = relationship("Country", back_populates="events")
    asset_impacts = relationship(
        "AssetImpact", back_populates="event", cascade="all, delete-orphan"
    )
    signals = relationship(
        "Signal",
        secondary=event_signals,
        back_populates="events",
    )
