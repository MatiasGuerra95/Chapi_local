"""T-232: endpoint /metrics (Prometheus). No requiere BD (los gauges de negocio se
saltan si la BD no responde; se exponen las métricas de proceso)."""
import asyncio

import httpx


def test_metrics_expone_prometheus():
    from app.main import app

    async def go():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
            # Genera al menos un request medido.
            await c.get("/health")
            r = await c.get("/metrics")
            assert r.status_code == 200
            assert "text/plain" in r.headers["content-type"]
            body = r.text
            assert "chapi_http_requests_total" in body
            # El request previo a /health quedó contabilizado.
            assert 'path="/health"' in body

    asyncio.run(go())
