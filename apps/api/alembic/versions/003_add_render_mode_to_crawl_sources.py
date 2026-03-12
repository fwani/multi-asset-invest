"""Add render_mode to crawl_sources.

Revision ID: 003
Revises: 002
Create Date: 2026-03-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "crawl_sources",
        sa.Column("render_mode", sa.String(length=32), nullable=False, server_default="static"),
    )


def downgrade() -> None:
    op.drop_column("crawl_sources", "render_mode")
