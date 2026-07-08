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
    """Crea las tablas si no existen (MVP; migrar a Alembic en fase 2)."""
    from app import models  # noqa: F401  (asegura registro de modelos en Base)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependencia FastAPI: entrega una sesión async por request."""
    async with SessionLocal() as session:
        yield session
