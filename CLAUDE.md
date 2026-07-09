# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Chapi Local: internal due-diligence & compliance tool for a Chilean HR/staffing company. It queries public Poder Judicial (OJV) records by name, persists normalized evidence, computes a rule-based risk score, and generates a traceable HTML report. Language of the domain/UI/reports is Spanish (Chile).

Status is MVP: the scraper is **mocked** behind a swappable interface; the real Playwright scraper, LLM summaries, and pgvector are deferred to phase 2. See `docs/requirements.md` (the "what", with IDs `RF-/RD-/RC-/RNF-/DD-`) and `docs/plan.md` (the "how").

## Session workflow (progress tracking — no reminders needed)

`docs/STATUS.md` is the single source of truth for "where we are". It is deliberately short (≤1 screen): current state, the next task, and blockers.

- **At the start of a session** — and whenever asked "¿en qué trabajamos ahora?" / "¿dónde quedamos?" — read `docs/STATUS.md` first and answer from it before doing project work.
- **After finishing any task**, immediately update `docs/STATUS.md` (bump the date, refresh "Ahora / próximo" and "Últimas tareas completadas") and tick that task's checkbox in `docs/tasks.md`. Keeping STATUS current after every task means it is always up to date at session close — there is no separate end-of-session step to remember.

Document roles: `STATUS.md` = live bookmark · `tasks.md` = backlog (`T-xx`, checkboxes) · `requirements.md` / `plan.md` = the what/how. Keep STATUS a pointer; never copy the backlog into it.

## Commands

The `app` package lives under `backend/`, so **`app.*` imports require `backend/` on the path**. This is the most common gotcha.

```bash
# Full stack (API + worker + Postgres + Redis)
cp .env.sample .env && docker compose up --build

# API locally (uvicorn adds backend/ to the path via --app-dir)
uvicorn app.main:app --reload --app-dir backend

# Worker locally (run from repo root: `workers` is at root, `app` is under backend/)
PYTHONPATH=backend arq workers.judicial_worker.WorkerSettings

# Tests (conftest.py injects backend/ onto sys.path — no env var needed)
pytest -q
pytest tests/test_risk_engine.py::test_niveles_por_score -q   # single test

# Lint (CI runs exactly this)
ruff check backend workers
```

CI (`.github/workflows/ci.yml`) runs: `ruff check backend workers`, `import app.main`, and `pytest` (all with `PYTHONPATH=backend`).

## Architecture (the big picture)

Async end-to-end: **FastAPI (async) → arq/Redis queue → worker → PostgreSQL (async, asyncpg)**. The API only orchestrates; the worker does the slow scraping. Never introduce sync DB/HTTP calls into this path.

Request flow (`backend/app/routers/consultas.py` → `workers/judicial_worker.py`):
1. `POST /consultas` validates, creates `Subject`+`Consulta(pending)`, writes an audit row, enqueues `run_consulta(id)`, returns `202`.
2. The worker's `run_consulta` marks `running`, streams cases from the scraper — **writing `results/{slug}.json` in real time** and inserting `CaseResult` rows — then computes the score and marks `done` (or `error`). Every step writes to `audit_logs`.
3. `GET /consultas/{id}` returns state+cases; `GET /consultas/{id}/report` renders the HTML report; `GET /audit` returns the trace.

Scraper is the key extension point (`backend/app/services/pjud_scraper.py`): `PjudScraper` is a `Protocol` whose `scan_persona(...)` is an **async generator of `CaseRecord` (a pure producer — it does not persist)**. `get_scraper()` returns `MockPjudScraper` or `PlaywrightPjudScraper` based on `USE_MOCK_SCRAPER`. The worker consumes the generator identically for either, so swapping mock→real touches neither the API nor the worker. Playwright is imported lazily so the mock path needs no browser. The real scraper is a skeleton ported from the reference scripts `crawler_nom.py` / `detalle.py` (at repo root); OJV competencia codes **Laboral=4 and Penal=5 are confirmed; Civil and Cobranza are placeholders that must be verified against the live DOM** (`COMPETENCIAS` in `backend/app/config.py`).

Persistence: `backend/app/db.py` creates tables via `Base.metadata.create_all` on startup by default (`AUTO_CREATE_TABLES=true`, used in dev/tests). **Alembic exists** (T-221) for production: set `AUTO_CREATE_TABLES=false` and run `alembic upgrade head` (config in `alembic.ini`, async `migrations/env.py`, initial migration under `migrations/versions/`). Models: `Subject 1─* Consulta 1─* CaseResult`, plus append-only `AuditLog` and `Report`; `Consulta.id` is a UUID and variable fields use JSONB.

## Compliance invariants (do not regress)

This is a compliance product; these are enforced in code and must stay true:
- **Legitimate purpose is mandatory.** `motivo` (≥10 chars, non-trivial) is validated in `schemas.ConsultaCreate` — no motive ⇒ HTTP 422 before anything is created.
- **Audit is append-only** and written on every lifecycle event via `services/audit_service.log_event` (never update/delete audit rows).
- **`risk_engine` outputs indicators only** — never culpability, never a hire/no-hire recommendation (there is a test asserting the report contains no such language).
- **Homonym flag**: name-only search ⇒ results carry `possible_homonym`; the report warns about it.
- The report template (`backend/app/templates/report.html.j2`) must keep its disclaimer.

## Conventions

- Keep generated/working files out of the repo root; docs go in `docs/`.
- Progress tracking lives in `docs/STATUS.md` + `docs/tasks.md` — see **Session workflow** above.
- `requirements.txt` is the MVP runtime; the heavy ML stack (llama-cpp, sentence-transformers, pgvector) is isolated in `requirements-ml.txt` for phase 2.
