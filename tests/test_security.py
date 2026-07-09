"""T-102: control de acceso mínimo por API key.

Prueba directa de la dependencia ``require_access`` (sin BD) y del cableado a
nivel router (401 antes de tocar la BD). El camino "clave correcta ⇒ pasa" a
endpoints reales se cubre en el smoke de stack completo (requiere Postgres).
"""
import asyncio

import httpx
import pytest
from fastapi import HTTPException

from app import security
from app.config import settings


def test_modo_abierto_sin_api_key(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "")
    assert security.require_access(x_api_key=None, authorization=None) == "anon"


def test_exige_clave_cuando_esta_configurada(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "s3cret")
    with pytest.raises(HTTPException) as exc:
        security.require_access(x_api_key=None, authorization=None)
    assert exc.value.status_code == 401


def test_acepta_x_api_key(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "s3cret")
    assert security.require_access(x_api_key="s3cret", authorization=None) == "api-key"


def test_acepta_bearer(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "s3cret")
    assert security.require_access(x_api_key=None, authorization="Bearer s3cret") == "api-key"


def test_rechaza_clave_incorrecta(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "s3cret")
    with pytest.raises(HTTPException):
        security.require_access(x_api_key="nope", authorization=None)


def test_router_gated_devuelve_401(monkeypatch):
    """El cableado a nivel router corta con 401 antes de tocar la BD."""
    monkeypatch.setattr(settings, "api_key", "s3cret")
    from app.main import app

    async def go():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
            assert (await c.get("/audit")).status_code == 401
            assert (await c.get("/audit", headers={"X-API-Key": "malo"})).status_code == 401
            # Health/readiness quedan abiertos (probes del orquestador).
            assert (await c.get("/health")).status_code == 200

    asyncio.run(go())
