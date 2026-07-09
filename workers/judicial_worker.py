"""Worker arq: procesa consultas de forma asíncrona.

Consume el scraper (mock o Playwright), escribe JSON en tiempo real por persona,
persiste causas normalizadas en Postgres, calcula el score y audita cada paso.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from arq.connections import RedisSettings

from app import models
from app.config import settings
from app.db import SessionLocal, init_models
from app.logging_config import configure_logging, set_job_id
from app.services import audit_service, risk_engine
from app.services.pjud_scraper import get_scraper, persona_slug

logger = logging.getLogger("app.worker")


def _sujeto(subject: models.Subject) -> str:
    nombre = f"{subject.nombre} {subject.ape_paterno} {subject.ape_materno}".strip()
    return f"{nombre} (rut={subject.rut or 'N/D'})"


async def run_consulta(ctx, consulta_id: str):
    cid = uuid.UUID(consulta_id)
    # Correlación: usa el job_id de arq; si se invoca directo (tests), el consulta_id.
    set_job_id(str(ctx.get("job_id") or consulta_id))
    logger.info("run_consulta_start", extra={"consulta_id": consulta_id})

    async with SessionLocal() as session:
        consulta = await session.get(models.Consulta, cid)
        if consulta is None:
            return {"status": "not_found", "consulta_id": consulta_id}
        subject = await session.get(models.Subject, consulta.subject_id)

        params = consulta.params or {}
        comps = params.get("competencias") or []
        year_from = params.get("year_from", settings.default_year_from)
        year_to = params.get("year_to", settings.default_year_to)

        slug = persona_slug(subject.nombre, subject.ape_paterno, subject.ape_materno)
        results_dir = Path(settings.results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)
        json_path = results_dir / f"{slug}.json"

        consulta.status = "running"
        consulta.started_at = datetime.utcnow()
        consulta.results_json_path = str(json_path)
        await audit_service.log_event(
            session,
            consulta_id=consulta.id,
            usuario=consulta.requested_by,
            motivo=consulta.motivo,
            sujeto=_sujeto(subject),
            fuente=consulta.fuente,
            action="consulta_iniciada",
            params=params,
        )
        await session.commit()

        records: list[dict] = []
        try:
            scraper = get_scraper()
            first = True
            # JSON en tiempo real: se escribe a medida que llega cada causa.
            with json_path.open("w", encoding="utf-8") as jf:
                jf.write("[\n")
                async for rec in scraper.scan_persona(
                    subject.nombre,
                    subject.ape_paterno,
                    subject.ape_materno,
                    comps,
                    year_from,
                    year_to,
                ):
                    if not first:
                        jf.write(",\n")
                    json.dump(rec, jf, ensure_ascii=False)
                    jf.flush()
                    first = False

                    session.add(
                        models.CaseResult(
                            consulta_id=consulta.id,
                            competencia=rec.get("competencia"),
                            rit=rec.get("rit"),
                            ruc=rec.get("ruc"),
                            tribunal=rec.get("tribunal"),
                            caratulado=rec.get("caratulado"),
                            fecha_ingreso=rec.get("fecha_ingreso"),
                            estado=rec.get("estado"),
                            year=rec.get("year"),
                            litigantes=rec.get("litigantes") or [],
                            relaciones=rec.get("relaciones") or [],
                            possible_homonym=bool(rec.get("possible_homonym")),
                            source_url=rec.get("source_url"),
                        )
                    )
                    await session.flush()
                    records.append(rec)
                jf.write("\n]\n")

            risk = risk_engine.compute_score(records)
            consulta.risk_score = risk["score"]
            consulta.risk_level = risk["level"]
            consulta.status = "done"
            consulta.finished_at = datetime.utcnow()
            await audit_service.log_event(
                session,
                consulta_id=consulta.id,
                usuario=consulta.requested_by,
                motivo=consulta.motivo,
                sujeto=_sujeto(subject),
                fuente=consulta.fuente,
                action="consulta_finalizada",
                params={"total": risk["total"], "score": risk["score"], "level": risk["level"]},
            )
            await session.commit()
            logger.info(
                "run_consulta_done",
                extra={"consulta_id": consulta_id, "total": risk["total"],
                       "score": risk["score"], "level": risk["level"]},
            )
            return {"status": "done", "total": risk["total"], "score": risk["score"]}

        except Exception as exc:  # noqa: BLE001
            logger.exception("run_consulta_error", extra={"consulta_id": consulta_id})
            await session.rollback()
            consulta = await session.get(models.Consulta, cid)
            consulta.status = "error"
            consulta.error = str(exc)[:2000]
            consulta.finished_at = datetime.utcnow()
            await audit_service.log_event(
                session,
                consulta_id=consulta.id,
                usuario=consulta.requested_by,
                motivo=consulta.motivo,
                sujeto=_sujeto(subject),
                fuente=consulta.fuente,
                action="consulta_error",
                params={"error": str(exc)[:500]},
            )
            await session.commit()
            raise


async def _startup(ctx):
    configure_logging()
    await init_models()


class WorkerSettings:
    functions = [run_consulta]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = _startup
    # El scraper real puede tardar (muchos tribunales × años); evita que arq
    # mate el job a los 300 s por defecto (part. de T-65).
    job_timeout = settings.arq_job_timeout_seconds
