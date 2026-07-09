"""T-211/T-212: gate del endpoint de búsqueda pgvector entre consultas.

El store persistente pgvector se verifica end-to-end contra la imagen
`pgvector/pgvector:pg16` (fuera de CI). Aquí sólo se cubre el gate por config, que
sí corre en CI sin pgvector instalado.
"""
import asyncio

import httpx

from app.config import settings


def test_search_similar_404_si_pgvector_desactivado():
    from app.main import app

    async def go():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
            # Default: enable_pgvector=False -> 404 (no requiere pgvector instalado).
            assert not settings.enable_pgvector
            r = await c.get("/search/similar?q=estafa")
            assert r.status_code == 404

    asyncio.run(go())
