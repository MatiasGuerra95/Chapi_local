"""Búsqueda semántica entre consultas sobre el store pgvector (T-211/T-212, escala).

OPT-IN: requiere ``ENABLE_PGVECTOR=true`` (imagen pgvector + ML stack). Con el flag
apagado responde 404. El import de ``vectorstore`` es perezoso para no exigir
``pgvector`` en el path por defecto.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.security import authorize

router = APIRouter(prefix="/search", tags=["search"], dependencies=[Depends(authorize)])


@router.get("/similar")
async def search_similar(
    q: str = Query(min_length=1, description="Texto a buscar semánticamente"),
    top: int = Query(default=5, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    if not (settings.enable_semantic_search and settings.enable_pgvector):
        raise HTTPException(status_code=404, detail="Búsqueda pgvector deshabilitada.")

    from app import vectorstore
    from app.services import embeddings_service

    qv = embeddings_service.get_embedder().embed(q)
    rows = await vectorstore.search(session, qv, top=top)
    return [
        {
            "distance": round(float(dist), 4),
            "consulta_id": str(ce.consulta_id),
            "case_id": ce.case_id,
            "texto": ce.texto,
        }
        for ce, dist in rows
    ]
