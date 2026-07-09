"""Endpoint de auditoría (trazabilidad)."""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db import get_session
from app.security import authorize

router = APIRouter(prefix="/audit", tags=["audit"], dependencies=[Depends(authorize)])


@router.get("", response_model=list[schemas.AuditOut])
async def listar_auditoria(
    consulta_id: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(models.AuditLog).order_by(models.AuditLog.created_at.desc())
    if consulta_id:
        try:
            cid = uuid.UUID(consulta_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de consulta inválido.")
        stmt = stmt.where(models.AuditLog.consulta_id == cid)
    result = await session.execute(stmt)
    return result.scalars().all()
