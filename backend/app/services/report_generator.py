"""Generación del informe HTML (Jinja2) con disclaimer y marca de homónimos."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings
from app.services import nlp_service

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "j2"]),
)


def render_report(*, consulta, subject, cases, risk: dict) -> str:
    """Renderiza el informe HTML. consulta/subject/cases pueden ser ORM o dicts."""
    template = _env.get_template("report.html.j2")
    return template.render(
        consulta=consulta,
        subject=subject,
        cases=cases,
        risk=risk,
        summary=nlp_service.generate_summary(cases, risk),
        fuente=settings.fuente,
        generated_at=datetime.utcnow(),
    )


def save_report(consulta_id, html: str) -> str:
    """Guarda el HTML en results/ y devuelve la ruta."""
    out_dir = Path(settings.results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{consulta_id}_report.html"
    path.write_text(html, encoding="utf-8")
    return str(path)
