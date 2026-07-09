"""T-83/T-84: integración API + worker contra Postgres real.

Se salta si no hay `DATABASE_URL` de Postgres (los tests unitarios no requieren DB).
Todo el flujo corre en un único event loop para evitar problemas de asyncpg entre loops.
"""
import asyncio
import os

import httpx
import pytest

DB = os.getenv("DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    "postgresql" not in DB, reason="requiere Postgres (definir DATABASE_URL)"
)


def test_flujo_completo_api_worker():
    from app.db import Base, engine, init_models
    from app.main import app
    from workers.judicial_worker import run_consulta

    async def flow():
        # Estado limpio
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await init_models()

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            # RC-01/RC-02: sin motivo válido -> 422
            r = await c.post("/consultas", json={
                "subject": {"nombre": "Ana", "ape_paterno": "Diaz"},
                "requested_by": "u", "motivo": "corto",
                "year_from": 2020, "year_to": 2021})
            assert r.status_code == 422

            # Crear -> 202 pending
            r = await c.post("/consultas", json={
                "subject": {"nombre": "Ana", "ape_paterno": "Diaz", "ape_materno": "Soto"},
                "requested_by": "reclutador",
                "motivo": "Debida diligencia previa a contratación",
                "competencias": ["Civil", "Penal"],
                "year_from": 2019, "year_to": 2021})
            assert r.status_code == 202
            cid = r.json()["id"]
            assert r.json()["status"] == "pending"

            # Worker (mock, sin Redis): procesa el job
            await run_consulta({}, cid)

            # Estado done + causas + score + homónimos
            d = (await c.get(f"/consultas/{cid}")).json()
            assert d["status"] == "done"
            assert len(d["cases"]) > 0
            assert d["risk_level"] in ("bajo", "medio", "alto")
            assert d["homonym_count"] > 0

            # Informe HTML con disclaimer
            r = await c.get(f"/consultas/{cid}/report")
            assert r.status_code == 200 and "Disclaimer legal" in r.text

            # Informe PDF (T-231): 200 con %PDF si hay navegador, o 503 si no está.
            rp = await c.get(f"/consultas/{cid}/report.pdf")
            assert rp.status_code in (200, 503)
            if rp.status_code == 200:
                assert rp.content[:4] == b"%PDF"

            # Auditoría del ciclo de vida
            actions = {a["action"] for a in (await c.get(f"/audit?consulta_id={cid}")).json()}
            assert {"consulta_creada", "consulta_iniciada",
                    "consulta_finalizada", "informe_generado"} <= actions

            # T-45: paginación (limit acota el número de filas)
            assert len((await c.get("/consultas?limit=1")).json()) <= 1
            assert len((await c.get(f"/audit?consulta_id={cid}&limit=2")).json()) <= 2

        await engine.dispose()

    asyncio.run(flow())
