"""Endpoints de consultas de due diligence."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.config import settings
from app.db import get_session
from app.logging_config import request_id_var
from app.security import authorize
from app.services import audit_service, embeddings_service, report_generator, risk_engine

router = APIRouter(
    prefix="/consultas", tags=["consultas"], dependencies=[Depends(authorize)]
)


def _sujeto_txt(subject: models.Subject) -> str:
    nombre = f"{subject.nombre} {subject.ape_paterno} {subject.ape_materno}".strip()
    return f"{nombre} (rut={subject.rut or 'N/D'})"


async def _get_consulta(session: AsyncSession, consulta_id: uuid.UUID, with_cases: bool = False):
    stmt = select(models.Consulta).where(models.Consulta.id == consulta_id)
    stmt = stmt.options(selectinload(models.Consulta.subject))
    if with_cases:
        stmt = stmt.options(selectinload(models.Consulta.cases))
    result = await session.execute(stmt)
    consulta = result.scalar_one_or_none()
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta no encontrada.")
    return consulta


def _parse_uuid(consulta_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(consulta_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de consulta inválido.")


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.ConsultaOut)
async def crear_consulta(
    payload: schemas.ConsultaCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    principal: str = Depends(authorize),
):
    """Crea una consulta (con finalidad legítima), audita y encola el scraping."""
    subject = models.Subject(**payload.subject.model_dump())
    session.add(subject)
    await session.flush()

    params = {
        "competencias": payload.competencias,
        "year_from": payload.year_from,
        "year_to": payload.year_to,
    }
    consulta = models.Consulta(
        subject_id=subject.id,
        requested_by=payload.requested_by,
        motivo=payload.motivo,
        fuente=settings.fuente,
        params=params,
        status="pending",
    )
    session.add(consulta)
    await session.flush()

    # T-105: reforzar la evidencia de finalidad legítima: además del motivo, se
    # registra el principal autenticado y el request-id de correlación de la petición.
    await audit_service.log_event(
        session,
        consulta_id=consulta.id,
        usuario=payload.requested_by,
        motivo=payload.motivo,
        sujeto=_sujeto_txt(subject),
        fuente=settings.fuente,
        action="consulta_creada",
        params={**params, "principal": principal, "request_id": request_id_var.get()},
    )
    await session.commit()

    pool = getattr(request.app.state, "arq_pool", None)
    if pool is not None:
        await pool.enqueue_job("run_consulta", str(consulta.id))

    return await _get_consulta(session, consulta.id)


@router.get("", response_model=list[schemas.ConsultaOut])
async def listar_consultas(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(models.Consulta)
        .options(selectinload(models.Consulta.subject))
        .order_by(models.Consulta.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{consulta_id}", response_model=schemas.ConsultaDetailOut)
async def obtener_consulta(consulta_id: str, session: AsyncSession = Depends(get_session)):
    cid = _parse_uuid(consulta_id)
    consulta = await _get_consulta(session, cid, with_cases=True)
    risk = risk_engine.compute_score(consulta.cases)
    detail = schemas.ConsultaDetailOut.model_validate(consulta)
    detail.cases = [schemas.CaseResultOut.model_validate(c) for c in consulta.cases]
    detail.counts = risk["counts"]
    detail.homonym_count = sum(1 for c in consulta.cases if c.possible_homonym)
    return detail


@router.get("/{consulta_id}/similar", response_model=list[schemas.SimilarCaseOut])
async def buscar_similares(
    consulta_id: str,
    q: str = Query(min_length=1, description="Texto a buscar semánticamente"),
    top: int = Query(default=5, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    """Búsqueda semántica sobre las causas de la consulta (T-212).

    Rankea en memoria por similitud coseno del embedding del texto ``q`` contra el
    de cada causa. Con `USE_MOCK_EMBEDDINGS=true` (default) usa un embedder léxico;
    la escala entre consultas con pgvector es el paso siguiente (fase 2).
    """
    if not settings.enable_semantic_search:
        raise HTTPException(status_code=404, detail="Búsqueda semántica deshabilitada.")
    cid = _parse_uuid(consulta_id)
    consulta = await _get_consulta(session, cid, with_cases=True)

    embedder = embeddings_service.get_embedder()
    qv = embedder.embed(q)
    scored = []
    for c in consulta.cases:
        texto = " ".join(
            str(x) for x in (c.caratulado, c.competencia, c.tribunal, c.estado) if x
        )
        sim = embeddings_service.cosine(qv, embedder.embed(texto))
        scored.append((sim, c))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [
        schemas.SimilarCaseOut(
            similarity=round(sim, 4), case=schemas.CaseResultOut.model_validate(c)
        )
        for sim, c in scored[:top]
    ]


@router.get("/{consulta_id}/report", response_class=HTMLResponse)
async def generar_informe(consulta_id: str, session: AsyncSession = Depends(get_session)):
    cid = _parse_uuid(consulta_id)
    consulta = await _get_consulta(session, cid, with_cases=True)

    risk = risk_engine.compute_score(consulta.cases)
    html = report_generator.render_report(
        consulta=consulta, subject=consulta.subject, cases=consulta.cases, risk=risk
    )
    path = report_generator.save_report(consulta.id, html)

    session.add(
        models.Report(
            consulta_id=consulta.id, html_path=path, score=risk["score"], level=risk["level"]
        )
    )
    await audit_service.log_event(
        session,
        consulta_id=consulta.id,
        usuario=consulta.requested_by,
        motivo=consulta.motivo,
        sujeto=_sujeto_txt(consulta.subject),
        fuente=consulta.fuente,
        action="informe_generado",
        params={"score": risk["score"], "level": risk["level"], "total": risk["total"]},
    )
    await session.commit()

    return HTMLResponse(content=html)
