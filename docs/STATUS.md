# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**M10 cerrado**; Fase 2 **F2.A** (scraper real + infra live), **F2.B** (NLP + semántica) y parte de **F2.C** en `main`. F2.C: `T-222` desambiguación de homónimos por RUT y `T-221` **Alembic** (async, migración inicial verificada contra Postgres real + integración E2E). `create_all` sigue de default; prod usa `AUTO_CREATE_TABLES=false` + `alembic upgrade head`. Verificado: ruff ✅ + pytest **66 passed / 1 skipped** (integración pasa contra Postgres real).

## Ahora / próximo
- **Docker OK** (3 fixes): creds `desktop.exe`, base `bookworm` (Playwright), healthcheck db con `-d`. Live build funciona.
- **Corrida en vivo (tú)** con `scripts/README-live-validation.md`: `inspect_ojv.py` → `T-200`; `validate_live.py` → `T-205`; `T-203` si algún detalle usa POST/JWT.
- **F2.C restante**: `T-223` consulta de **empresas** (razón social/RUT). `T-220` (auth) ya hecha.
- Para activar auth: `AUTH_ENABLED=true` + `JWT_SECRET` + crear admin con `scripts/create_user.py`.
- **Pendiente F2.B**: store pgvector persistente entre consultas (requiere ML stack).
- ⚠️ `.gitignore` local mantiene `/docs` — nuevos docs con `git add -f`.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): ✅ **cerrado** — código `T-22`/`T-46`/`T-102`/`T-103`/`T-104`/`T-105` + legal `T-100`/`T-101`
- Fase 2: 🟡 **F2.A** (`T-201/202/204`; live pendiente `T-200/203/205`) · **F2.B** `T-210`/`T-212` ✅, `T-211` embeddings+overlay ✅ (store pgvector pendiente) · **F2.C** `T-220` auth ✅ + `T-221` Alembic ✅ + `T-222` RUT ✅; `T-223` empresas pendiente · F2.D no iniciada

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.
- `T-104`/`T-65`/`T-66` se difieren para acompañar el scraper real (Fase 2), donde tienen efecto real.

## Últimas tareas completadas
- `T-220` **auth de usuarios** (User + pbkdf2 + JWT + RBAC + gate `authorize` + migración `b7decc69951e`), verificado E2E contra Postgres real (+9 tests)
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
