"""T-220: flujo de auth end-to-end contra Postgres real.

Se salta sin `DATABASE_URL` de Postgres. Cubre login, /me, RBAC y el gate de los
endpoints de negocio con AUTH_ENABLED.
"""
import asyncio
import os

import httpx
import pytest

DB = os.getenv("DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    "postgresql" not in DB, reason="requiere Postgres (definir DATABASE_URL)"
)


def test_flujo_auth():
    from app import models
    from app.config import settings
    from app.db import Base, SessionLocal, engine, init_models
    from app.main import app
    from app.services import auth_service

    settings.jwt_secret = "itest-secret-de-32-bytes-o-mas-para-hs256"
    prev_auth = settings.auth_enabled

    async def flow():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await init_models()

        # Admin sembrado directamente.
        async with SessionLocal() as s:
            s.add(models.User(
                username="admin", role="admin",
                password_hash=auth_service.hash_password("admin-super-clave")))
            await s.commit()

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
            # Login OK
            r = await c.post("/auth/token",
                             json={"username": "admin", "password": "admin-super-clave"})
            assert r.status_code == 200
            admin_tok = r.json()["access_token"]

            # Credenciales inválidas -> 401
            assert (await c.post("/auth/token",
                    json={"username": "admin", "password": "mala"})).status_code == 401

            # /me sin token -> 401; con token -> 200 admin
            assert (await c.get("/auth/me")).status_code == 401
            me = await c.get("/auth/me", headers={"Authorization": f"Bearer {admin_tok}"})
            assert me.status_code == 200 and me.json()["role"] == "admin"

            # Admin crea un analyst
            r = await c.post("/auth/users",
                             headers={"Authorization": f"Bearer {admin_tok}"},
                             json={"username": "ana", "password": "analyst-clave", "role": "analyst"})
            assert r.status_code == 201
            ana_tok = (await c.post("/auth/token",
                       json={"username": "ana", "password": "analyst-clave"})).json()["access_token"]

            # Analyst NO puede crear usuarios -> 403
            assert (await c.post("/auth/users",
                    headers={"Authorization": f"Bearer {ana_tok}"},
                    json={"username": "x", "password": "12345678", "role": "analyst"})
                    ).status_code == 403

            # Con AUTH_ENABLED, el endpoint de negocio exige JWT.
            settings.auth_enabled = True
            payload = {"subject": {"nombre": "Juan", "ape_paterno": "Perez"},
                       "requested_by": "ana",
                       "motivo": "Debida diligencia previa a contratación",
                       "competencias": ["Penal"], "year_from": 2020, "year_to": 2020}
            assert (await c.post("/consultas", json=payload)).status_code == 401
            r = await c.post("/consultas", json=payload,
                             headers={"Authorization": f"Bearer {ana_tok}"})
            assert r.status_code == 202

    try:
        asyncio.run(flow())
    finally:
        settings.auth_enabled = prev_auth
        asyncio.run(engine.dispose())
