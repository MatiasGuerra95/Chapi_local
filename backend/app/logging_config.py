"""Logging estructurado (JSON) con correlación por request-id / job-id.

Trazabilidad técnica (T-103, RNF): cada línea de log lleva el identificador de
correlación del contexto actual —``request_id`` en la API, ``job_id`` en el
worker— para poder seguir una consulta de punta a punta a través de los procesos.

Sin dependencias extra: usa sólo ``logging`` y ``json`` de la stdlib.
"""
from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar

# Contexto de correlación. Se propaga por corrutina/tarea vía contextvars.
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
job_id_var: ContextVar[str | None] = ContextVar("job_id", default=None)

# Campos estándar de LogRecord que no reinyectamos como "extra".
_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "message",
    "asctime",
    "taskName",
}


def new_request_id() -> str:
    """Genera un identificador de correlación nuevo."""
    return uuid.uuid4().hex


def set_request_id(value: str | None) -> None:
    request_id_var.set(value)


def set_job_id(value: str | None) -> None:
    job_id_var.set(value)


class CorrelationFilter(logging.Filter):
    """Inyecta ``request_id`` y ``job_id`` del contexto en cada registro."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.job_id = job_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    """Formatea cada registro como una línea JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "job_id": getattr(record, "job_id", None),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Campos "extra" arbitrarios pasados por el caller (logger.info(..., extra=...)).
        for key, value in record.__dict__.items():
            if key not in _RESERVED and key not in payload:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False, default=str)


_configured = False


def configure_logging(level: int | str = logging.INFO) -> None:
    """Configura el logging JSON en el logger raíz. Idempotente."""
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(CorrelationFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # uvicorn/arq traen sus propios handlers; que propaguen al raíz evita duplicados.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "arq"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

    _configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
