"""Lógica compartida de creación de consultas (usada por la API y la UI, T-230).

Mantiene las invariantes de compliance en un solo lugar: valida vía
``schemas.ConsultaCreate`` (motivo obligatorio, RC-01), persiste sujeto+consulta y
escribe la auditoría (RC-05) antes del commit.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.config import settings
from app.logging_config import request_id_var
from app.services import audit_service


def sujeto_txt(subject: models.Subject) -> str:
    nombre = f"{subject.nombre} {subject.ape_paterno} {subject.ape_materno}".strip()
    return f"{nombre} (rut={subject.rut or 'N/D'})"


async def create_consulta(
    session: AsyncSession, payload: schemas.ConsultaCreate, principal: str
) -> models.Consulta:
    """Crea sujeto+consulta y audita el evento. El caller encola el job."""
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

    await audit_service.log_event(
        session,
        consulta_id=consulta.id,
        usuario=payload.requested_by,
        motivo=payload.motivo,
        sujeto=sujeto_txt(subject),
        fuente=settings.fuente,
        action="consulta_creada",
        params={**params, "principal": principal, "request_id": request_id_var.get()},
    )
    await session.commit()
    return consulta


async def enqueue(app, consulta_id) -> None:
    """Encola el job de scraping si hay pool de arq (Redis) disponible."""
    pool = getattr(app.state, "arq_pool", None)
    if pool is not None:
        await pool.enqueue_job("run_consulta", str(consulta_id))
