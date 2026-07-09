"""Motor async de SQLAlchemy, sesión y creación de tablas (MVP)."""
from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_models() -> None:
    """Crea las tablas si no existen (MVP; migrar a Alembic en fase 2).

    La API y el worker arrancan a la vez; ``create_all`` (check-then-create) no es
    atómico entre conexiones, por lo que se ignora la carrera de creación concurrente.

    En producción se recomienda ``AUTO_CREATE_TABLES=false`` y gestionar el esquema
    con Alembic (T-221).
    """
    from sqlalchemy.exc import IntegrityError, ProgrammingError

    from app import models  # noqa: F401  (asegura registro de modelos en Base)

    if not settings.auto_create_tables:
        return

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except (IntegrityError, ProgrammingError):
        # Otro proceso creó las tablas concurrentemente al arrancar; es benigno.
        pass


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependencia FastAPI: entrega una sesión async por request."""
    async with SessionLocal() as session:
        yield session
