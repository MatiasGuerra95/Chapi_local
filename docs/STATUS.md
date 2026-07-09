# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**Todo el backlog codeable está cerrado.** MVP + M10 + Fase 2 **F2.B/C/D** completas; **F2.A** con código+infra listos (falta la corrida en vivo). Última tanda (limpieza de `tasks.md`): `T-23` namespacing JSON, `T-33` normalización de nombre, `T-45` paginación, `T-65` reintentos arq, `T-66` commit por lotes, `T-74` doc backup, `T-86` script demo. Verificado: ruff ✅ + pytest **87 passed / 3 skipped** (3 integraciones contra Postgres real). **Sólo quedan pendientes las tareas que dependen de terceros** (ver abajo).

## Ahora / próximo — sólo pendientes que dependen de ti/terceros
- **T-05** — sign-off de RRHH/legal sobre requisitos (no codeable).
- **T-200/T-203/T-205** + residuo de **T-222** — requieren el **sitio en vivo** de la OJV. Todo listo: `scripts/README-live-validation.md` (`inspect_ojv.py` → `T-200`; `validate_live.py` → `T-205`).
- Demo local rápida: `docker compose up -d` → `python scripts/demo.py`.
- pgvector opt-in: `docker compose -f docker-compose.yml -f docker-compose.pgvector.yml up --build` → `GET /search/similar?q=`.
- UI en `GET /ui`; métricas en `GET /metrics`; PDF en `GET /consultas/{id}/report.pdf` (requiere imagen con `INSTALL_BROWSERS=true`).
- Para activar auth: `AUTH_ENABLED=true` + `JWT_SECRET` (≥32B) + `scripts/create_user.py`.
- ⚠️ `.gitignore` local mantiene `/docs` — nuevos docs con `git add -f`.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): ✅ **cerrado** — código `T-22`/`T-46`/`T-102`/`T-103`/`T-104`/`T-105` + legal `T-100`/`T-101`
- Fase 2: 🟡 **F2.A** (`T-201/202/204`; live pendiente `T-200/203/205`) · **F2.B completa** ✅ (`T-210`/`T-211` store pgvector/`T-212`) · **F2.C completa** ✅ · **F2.D completa** ✅

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.
- `T-104`/`T-65`/`T-66` se difieren para acompañar el scraper real (Fase 2), donde tienen efecto real.

## Últimas tareas completadas
- **Cierre de backlog codeable**: `T-23` JSON namespacing, `T-33` normalización nombre, `T-45` paginación, `T-65` reintentos, `T-66` commit por lotes, `T-74` doc backup, `T-86` script demo (+6 tests)
- `T-211` **store pgvector persistente** (`vectorstore.py` opt-in, worker indexa, `GET /search/similar`), verificado E2E contra `pgvector/pgvector:pg16`
- **F2.D completa**: `T-230` UI, `T-231` PDF, `T-232` `/metrics`, `T-233` evaluación de fuentes
- `T-220`/`T-221`/`T-222`/`T-223` **F2.C** (auth JWT+RBAC, Alembic, homónimos por RUT, empresas), verificadas contra Postgres real
- `T-220` **auth de usuarios** (User + pbkdf2 + JWT + RBAC + migración `b7decc69951e`), verificado E2E contra Postgres real
- `T-221` **Alembic** + `T-222` **homónimos por RUT** (verificados contra Postgres real)
- **Fix Docker**: `credsStore` roto en `~/.docker/config.json` + base Dockerfile → `python:3.12-slim-bookworm` (Playwright deps)
- `T-210`/`T-211`/`T-212` **Fase 2 F2.B**: síntesis NLP, `embeddings_service`, endpoint `/similar` y overlay pgvector
- `T-201`/`T-202`/`T-204` **Fase 2 F2.A**: scraper real abre modal de detalle, parsea litigantes/relaciones por sufijo, robustez (retry/user-agent) (+6 tests)
- `T-100`/`T-101` **revisión legal cerrada** (decisiones del responsable, `ff8b8c0`)
- `T-104` **politeness/rate limiting** (`RateLimiter` + `retry_async`, `6126ff2`)
- `T-102`/`T-105` **compliance M10**: API key + `motivo` endurecido y evidencia de propósito (`043d6ec`)

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
