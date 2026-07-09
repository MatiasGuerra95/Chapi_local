"""T-230: UI mínima end-to-end contra Postgres real (se salta sin DATABASE_URL)."""
import asyncio
import os

import httpx
import pytest

DB = os.getenv("DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    "postgresql" not in DB, reason="requiere Postgres (definir DATABASE_URL)"
)


def test_ui_flujo():
    from app.db import Base, engine, init_models
    from app.main import app
    from workers.judicial_worker import run_consulta

    async def flow():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await init_models()

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://t", follow_redirects=False
        ) as c:
            # Home renderiza
            r = await c.get("/ui")
            assert r.status_code == 200 and "nueva consulta" in r.text

            # Motivo trivial -> 422 con banner de error, sin crear
            bad = await c.post("/ui/consultas", data={
                "tipo": "persona", "nombre": "Ana", "ape_paterno": "Diaz",
                "requested_by": "recl", "motivo": "corto",
                "competencias": ["Penal"], "year_from": 2020, "year_to": 2020})
            assert bad.status_code == 422 and "No se pudo crear" in bad.text

            # Alta válida -> 303 redirect a la ficha
            ok = await c.post("/ui/consultas", data={
                "tipo": "persona", "nombre": "Ana", "ape_paterno": "Diaz",
                "requested_by": "recl",
                "motivo": "Debida diligencia previa a contratación",
                "competencias": ["Penal", "Civil"], "year_from": 2020, "year_to": 2021})
            assert ok.status_code == 303
            loc = ok.headers["location"]
            assert loc.startswith("/ui/consultas/")
            cid = loc.rsplit("/", 1)[1]

            # Ficha en estado pending
            d = await c.get(loc)
            assert d.status_code == 200 and "pending" in d.text

            # Procesa (mock) y la ficha muestra done + enlace al informe
            await run_consulta({}, cid)
            d2 = await c.get(loc)
            assert d2.status_code == 200
            assert "done" in d2.text
            assert f"/consultas/{cid}/report" in d2.text

        await engine.dispose()

    asyncio.run(flow())
