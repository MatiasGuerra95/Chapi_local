"""UI mínima server-rendered para reclutadores (T-230).

Presentación fina sobre la misma lógica de negocio: la creación reutiliza
``consulta_service.create_consulta`` (motivo obligatorio + auditoría, compliance).
Pensada para operar detrás del perímetro corporativo; el control de acceso por
usuario del API JSON se gobierna con ``AUTH_ENABLED`` (T-220).
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.config import COMPETENCIAS, settings
from app.db import get_session
from app.services import consulta_service, risk_engine

router = APIRouter(tags=["ui"])

_UI_DIR = Path(__file__).resolve().parent.parent / "templates" / "ui"
_env = Environment(
    loader=FileSystemLoader(str(_UI_DIR)), autoescape=select_autoescape(["html", "j2"])
)


def _page(name: str, status_code: int = 200, **ctx) -> HTMLResponse:
    ctx.setdefault("competencias_all", list(COMPETENCIAS))
    ctx.setdefault("default_year_from", settings.default_year_from)
    ctx.setdefault("default_year_to", settings.default_year_to)
    return HTMLResponse(_env.get_template(name).render(**ctx), status_code=status_code)


async def _recientes(session: AsyncSession, limit: int = 50):
    stmt = (
        select(models.Consulta)
        .options(selectinload(models.Consulta.subject))
        .order_by(models.Consulta.created_at.desc())
        .limit(limit)
    )
    return (await session.execute(stmt)).scalars().all()


@router.get("/ui", response_class=HTMLResponse)
async def home(session: AsyncSession = Depends(get_session)):
    return _page("index.html.j2", consultas=await _recientes(session), error=None, form={})


@router.post("/ui/consultas")
async def crear(
    request: Request,
    session: AsyncSession = Depends(get_session),
    tipo: str = Form("persona"),
    nombre: str = Form(""),
    ape_paterno: str = Form(""),
    ape_materno: str = Form(""),
    rut: str = Form(""),
    razon_social: str = Form(""),
    requested_by: str = Form(""),
    motivo: str = Form(""),
    competencias: list[str] = Form(default=[]),
    year_from: int = Form(settings.default_year_from),
    year_to: int = Form(settings.default_year_to),
):
    form = {
        "tipo": tipo, "nombre": nombre, "ape_paterno": ape_paterno,
        "ape_materno": ape_materno, "rut": rut, "razon_social": razon_social,
        "requested_by": requested_by, "motivo": motivo,
        "competencias": competencias, "year_from": year_from, "year_to": year_to,
    }
    try:
        payload = schemas.ConsultaCreate(
            subject={
                "tipo": tipo, "nombre": nombre, "ape_paterno": ape_paterno,
                "ape_materno": ape_materno, "rut": rut or None,
                "razon_social": razon_social or None,
            },
            requested_by=requested_by,
            motivo=motivo,
            competencias=competencias or list(COMPETENCIAS),
            year_from=year_from,
            year_to=year_to,
        )
    except ValidationError as exc:
        errores = "; ".join(e["msg"] for e in exc.errors())
        return _page(
            "index.html.j2", status_code=422,
            consultas=await _recientes(session), error=errores, form=form,
        )

    consulta = await consulta_service.create_consulta(session, payload, principal="ui")
    await consulta_service.enqueue(request.app, consulta.id)
    return RedirectResponse(url=f"/ui/consultas/{consulta.id}", status_code=303)


@router.get("/ui/consultas/{consulta_id}", response_class=HTMLResponse)
async def detalle(consulta_id: str, session: AsyncSession = Depends(get_session)):
    try:
        cid = uuid.UUID(consulta_id)
    except ValueError:
        return _page("detail.html.j2", status_code=400, consulta=None, error="ID inválido.")
    stmt = (
        select(models.Consulta)
        .where(models.Consulta.id == cid)
        .options(selectinload(models.Consulta.subject), selectinload(models.Consulta.cases))
    )
    consulta = (await session.execute(stmt)).scalar_one_or_none()
    if consulta is None:
        return _page("detail.html.j2", status_code=404, consulta=None, error="No encontrada.")
    risk = risk_engine.compute_score(consulta.cases)
    return _page("detail.html.j2", consulta=consulta, risk=risk, error=None)
