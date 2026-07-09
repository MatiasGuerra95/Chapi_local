"""T-46 (readiness) y T-103 (correlación request-id).

No requieren infraestructura: usan ``httpx.ASGITransport`` sin disparar el
lifespan, por lo que ``arq_pool`` es ``None`` (redis "unavailable") y la BD puede
no estar disponible. Por eso se aserta la *forma* del readiness (y que sea 200 o
503 de forma coherente), no un estado concreto que dependa del entorno.
"""
import asyncio

import httpx


def _client():
    from app.main import app

    return httpx.ASGITransport(app=app)


def test_health_liveness_y_request_id_generado():
    async def go():
        async with httpx.AsyncClient(transport=_client(), base_url="http://t") as c:
            r = await c.get("/health")
            assert r.status_code == 200
            assert r.json() == {"status": "ok"}
            # T-103: la respuesta lleva un request-id de correlación generado.
            rid = r.headers.get("X-Request-ID")
            assert rid and len(rid) >= 16

    asyncio.run(go())


def test_request_id_se_propaga_desde_el_header():
    async def go():
        async with httpx.AsyncClient(transport=_client(), base_url="http://t") as c:
            r = await c.get("/health", headers={"X-Request-ID": "corr-123"})
            assert r.status_code == 200
            # Si el cliente envía X-Request-ID, se respeta y se devuelve igual.
            assert r.headers.get("X-Request-ID") == "corr-123"

    asyncio.run(go())


def test_readiness_forma_y_codigo():
    async def go():
        async with httpx.AsyncClient(transport=_client(), base_url="http://t") as c:
            r = await c.get("/health/ready")
            # 200 sólo si DB y Redis responden; 503 en caso contrario.
            assert r.status_code in (200, 503)
            body = r.json()
            assert body["status"] in ("ready", "not_ready")
            assert set(body["checks"]) == {"database", "redis"}
            assert (r.status_code == 200) == (body["status"] == "ready")
            assert r.headers.get("X-Request-ID")

    asyncio.run(go())
