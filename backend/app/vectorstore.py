"""Store persistente de embeddings con pgvector (T-211, escala F2.B).

**OPT-IN**: sólo se usa con ``ENABLE_PGVECTOR=true`` + imagen Postgres con la
extensión (``docker-compose.pgvector.yml``) + el stack ML (``requirements-ml.txt``,
trae ``pgvector``). Este módulo **no** se importa en el path por defecto, para no
exigir ``pgvector`` en dev/tests: usa un metadata propio (``VectorBase``), separado
del ``Base`` del core, así que no toca ``create_all`` ni las migraciones Alembic.

La dimensión de la columna se fija con ``settings.embedding_dim`` y debe coincidir
con el modelo de embeddings (64 mock / 384 all-MiniLM-L6-v2). Cambiar de modelo con
otra dimensión requiere recrear la tabla.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, Text, func, select, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings


class VectorBase(DeclarativeBase):
    pass


class CaseEmbedding(VectorBase):
    __tablename__ = "case_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    consulta_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    case_id: Mapped[int] = mapped_column(Integer, index=True)
    texto: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


def case_text(case) -> str:
    """Texto representativo de una causa para indexar/buscar."""
    get = (lambda k: case.get(k)) if isinstance(case, dict) else (lambda k: getattr(case, k, None))
    return " ".join(str(x) for x in (get("caratulado"), get("competencia"),
                                     get("tribunal"), get("estado")) if x)


async def ensure_schema(engine: AsyncEngine) -> None:
    """Crea la extensión y la tabla de embeddings (idempotente)."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(VectorBase.metadata.create_all)


async def index_cases(session: AsyncSession, consulta_id, cases, embedder) -> int:
    """Persiste el embedding de cada causa. Devuelve cuántas indexó."""
    n = 0
    for c in cases:
        texto = case_text(c)
        if not texto:
            continue
        session.add(CaseEmbedding(
            consulta_id=consulta_id,
            case_id=getattr(c, "id", None) or (c.get("id") if isinstance(c, dict) else None) or 0,
            texto=texto,
            embedding=embedder.embed(texto),
        ))
        n += 1
    await session.commit()
    return n


async def search(session: AsyncSession, query_embedding, top: int = 5, consulta_id=None):
    """Búsqueda por distancia coseno pgvector. Devuelve [(CaseEmbedding, distance)]."""
    dist = CaseEmbedding.embedding.cosine_distance(query_embedding)
    stmt = select(CaseEmbedding, dist.label("distance"))
    if consulta_id is not None:
        stmt = stmt.where(CaseEmbedding.consulta_id == consulta_id)
    stmt = stmt.order_by(dist).limit(top)
    return [(row[0], row[1]) for row in (await session.execute(stmt)).all()]
