"""Asset model (investment target: stock, crypto, fx, etc.)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    currency_id: Mapped[int | None] = mapped_column(
        ForeignKey("currencies.id", ondelete="SET NULL"), nullable=True
    )
    exchange: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sector_id: Mapped[int | None] = mapped_column(
        ForeignKey("sectors.id", ondelete="SET NULL"), nullable=True
    )
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    currency = relationship("Currency", back_populates="assets")
    sector = relationship("Sector", back_populates="assets")
    country = relationship("Country", back_populates="assets")
    asset_impacts = relationship(
        "AssetImpact", back_populates="asset", cascade="all, delete-orphan"
    )
    signals = relationship("Signal", back_populates="asset", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="asset")
    orders = relationship("Order", back_populates="asset")
