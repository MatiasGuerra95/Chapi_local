"""Servicio de auditoría append-only (trazabilidad de consultas)."""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def log_event(
    session: AsyncSession,
    *,
    usuario: str,
    sujeto: str,
    fuente: str,
    action: str,
    consulta_id: Optional[uuid.UUID] = None,
    motivo: Optional[str] = None,
    params: Optional[dict] = None,
) -> AuditLog:
    """Inserta una entrada de auditoría. El caller es responsable del commit."""
    entry = AuditLog(
        consulta_id=consulta_id,
        usuario=usuario,
        motivo=motivo,
        sujeto=sujeto,
        fuente=fuente,
        action=action,
        params=params or {},
    )
    session.add(entry)
    await session.flush()
    return entry
