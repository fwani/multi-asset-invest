"""Minimal Asset model for worker (read assets.id for impact stub)."""

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
