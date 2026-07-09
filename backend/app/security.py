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

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.config import settings
from app.db import get_session
from app.services import auth_service

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


# ─── Autenticación de usuarios (T-220) ─────────────────────────────────────
def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization[len("bearer "):].strip()


async def _user_from_bearer(authorization: str | None, session: AsyncSession) -> models.User:
    import jwt

    token = _bearer_token(authorization)
    try:
        payload = auth_service.decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    user = (
        await session.execute(select(models.User).where(models.User.username == username))
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no válido.")
    return user


async def get_current_user(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> models.User:
    """Dependencia: usuario autenticado por JWT (para /auth y RBAC)."""
    return await _user_from_bearer(authorization, session)


def require_role(*roles: str):
    """Factory de dependencia: exige que el usuario tenga uno de ``roles``."""

    async def _dep(user: models.User = Depends(get_current_user)) -> models.User:
        if roles and user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes.")
        return user

    return _dep


async def authorize(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> str:
    """Gate de los endpoints de negocio: JWT de usuario si AUTH_ENABLED, si no API key.

    Devuelve el principal (``user:<username>`` o el de ``require_access``).
    """
    if settings.auth_enabled:
        user = await _user_from_bearer(authorization, session)
        return f"user:{user.username}"
    return require_access(x_api_key=x_api_key, authorization=authorization)
