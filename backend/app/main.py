"""Aplicación FastAPI de Chapi Local (due diligence & compliance)."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_models
from app.routers import audit, consultas, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea tablas (MVP) y abre el pool de arq (Redis) para encolar consultas.
    await init_models()
    app.state.arq_pool = None
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    except Exception:
        # Sin Redis disponible la API sigue operativa; el worker no recibirá jobs.
        app.state.arq_pool = None
    yield
    pool = getattr(app.state, "arq_pool", None)
    if pool is not None:
        await pool.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health.router)
app.include_router(consultas.router)
app.include_router(audit.router)
