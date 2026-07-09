"""Métricas Prometheus (T-232, observabilidad).

Expuestas en ``GET /metrics`` (proceso API). Los contadores de requests se
alimentan desde el middleware; los gauges de negocio (consultas por estado, causas)
se calculan desde la BD en cada scrape para dar visibilidad entre procesos
(la API y el worker son procesos separados).
"""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

REQUESTS = Counter(
    "chapi_http_requests_total",
    "Total de requests HTTP.",
    ["method", "path", "status"],
)

REQUEST_DURATION = Histogram(
    "chapi_http_request_duration_seconds",
    "Duración de los requests HTTP.",
    ["method", "path"],
)

CONSULTAS = Gauge(
    "chapi_consultas",
    "Consultas por estado (calculado desde la BD).",
    ["status"],
)

CASES = Gauge(
    "chapi_case_results_total",
    "Total de causas persistidas (calculado desde la BD).",
)
