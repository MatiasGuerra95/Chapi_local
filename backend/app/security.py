"""Control de acceso mínimo por API key (T-102, RC-08).

DD-05: el MVP no tiene autenticación de usuarios (queda para fase 2, T-220). Este
control es **proporcionado y activable por configuración**:

- Si ``settings.api_key`` está vacío ⇒ modo abierto (dev/MVP), se registra una
  advertencia una sola vez. Preserva el comportamiento actual y los tests.
- Si está definido ⇒ los endpoints de negocio exigen la clave en el header
  ``X-API-Key`` o ``Authorization: Bearer <clave>``; si falta o no coincide ⇒ 401.

La identidad por-usuario y el RBAC son fase 2 (T-220). Health/readiness quedan
abiertos a propósito para los probes del orquestador.
"""
from __future__ import annotations

import logging
import secrets

from fastapi import Header, HTTPException, status

from app.config import settings

logger = logging.getLogger("app.security")

_warned_open = False


def require_access(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> str:
    """Dependencia FastAPI. Devuelve el principal ("api-key" o "anon" en modo abierto)."""
    expected = (settings.api_key or "").strip()

    if not expected:
        global _warned_open
        if not _warned_open:
            logger.warning("access_control_open",
                           extra={"detail": "API_KEY no configurada; modo abierto (MVP)"})
            _warned_open = True
        return "anon"

    provided = x_api_key
    if not provided and authorization and authorization.lower().startswith("bearer "):
        provided = authorization[len("bearer "):].strip()

    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credencial de acceso inválida o ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "api-key"
