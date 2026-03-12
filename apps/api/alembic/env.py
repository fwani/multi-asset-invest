"""Alembic environment. Uses DATABASE_URL; sync driver for migrations."""

import os
import sys
from pathlib import Path

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Ensure api src is on path so "models" can be imported
_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from models.base import Base
import models  # noqa: F401 — load all models so metadata is complete

target_metadata = Base.metadata

# Prefer DATABASE_URL; convert async URL to sync for Alembic
_db_url = os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
if _db_url and _db_url.startswith("postgresql+asyncpg://"):
    _db_url = _db_url.replace("postgresql+asyncpg://", "postgresql://", 1)


def run_migrations_offline() -> None:
    url = _db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _db_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
