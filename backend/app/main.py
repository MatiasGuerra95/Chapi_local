"""Aplicación FastAPI de Chapi Local (due diligence & compliance)."""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.config import settings
from app.db import init_models
from app.logging_config import configure_logging, new_request_id, set_request_id
from app.routers import audit, consultas, health

configure_logging()
logger = logging.getLogger("app.request")


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


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    """Asigna/propaga un request-id de correlación y registra cada request."""
    request_id = request.headers.get("X-Request-ID") or new_request_id()
    set_request_id(request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "request_error",
            extra={"method": request.method, "path": request.url.path,
                   "elapsed_ms": round(elapsed_ms, 1)},
        )
        raise
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request",
        extra={"method": request.method, "path": request.url.path,
               "status": response.status_code, "elapsed_ms": round(elapsed_ms, 1)},
    )
    return response


app.include_router(health.router)
app.include_router(consultas.router)
app.include_router(audit.router)
