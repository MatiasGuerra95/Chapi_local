"""Endpoints de salud: liveness (`/health`) y readiness (`/health/ready`)."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session

router = APIRouter(tags=["health"])
logger = logging.getLogger("app.health")


@router.get("/health")
async def health():
    """Liveness: el proceso está vivo (no comprueba dependencias)."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(request: Request, session: AsyncSession = Depends(get_session)):
    """Readiness (T-46, RNF-07): comprueba conectividad a Postgres y Redis.

    Devuelve 200 si ambas dependencias responden; 503 si alguna falla, con el
    detalle por componente para diagnóstico.
    """
    checks: dict[str, str] = {}

    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("readiness_db_fail", extra={"error": str(exc)[:200]})
        checks["database"] = "error"

    pool = getattr(request.app.state, "arq_pool", None)
    if pool is None:
        checks["redis"] = "unavailable"
    else:
        try:
            await pool.ping()
            checks["redis"] = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.warning("readiness_redis_fail", extra={"error": str(exc)[:200]})
            checks["redis"] = "error"

    ready = all(v == "ok" for v in checks.values())
    body = {"status": "ready" if ready else "not_ready", "checks": checks}
    return JSONResponse(body, status_code=200 if ready else 503)
