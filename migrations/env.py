"""Entorno de Alembic (async) para Chapi Local (T-221).

Toma la metadata de los modelos SQLAlchemy y la URL desde ``app.config.settings``.
Ejecuta migraciones online con el engine async (asyncpg).
"""
from __future__ import annotations

import asyncio
import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Expone el paquete `app` (vive bajo backend/).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "backend"))

from app import models  # noqa: E402,F401  (registra los modelos en Base.metadata)
from app.config import settings  # noqa: E402
from app.db import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(settings.database_url, future=True)
    async with engine.connect() as connection:
        await connection.run_sync(_do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
