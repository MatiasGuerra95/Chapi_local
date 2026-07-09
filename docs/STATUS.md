# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**M10 cerrado**; **Fase 2 F2.A** (scraper real + infra de validación en vivo) y **F2.B** (NLP + búsqueda semántica) implementadas en `main`. NLP `T-210` (síntesis mock + skeleton llama-cpp), embeddings `T-211` (mock + overlay pgvector) y endpoint semántico `T-212` (`/consultas/{id}/similar`). Verificado: ruff ✅ + import ✅ + pytest **51 passed / 1 skipped**.

## Ahora / próximo
- **Docker arreglado**: `~/.docker/config.json` tenía `credsStore: desktop.exe` roto (WSL) → removido (backup en `config.json.bak`). El build ya resuelve imágenes públicas.
- **Corrida en vivo (tú)** con `scripts/README-live-validation.md`: `inspect_ojv.py` → cerrar `T-200`; `validate_live.py` → cerrar `T-205`; `T-203` si algún detalle usa POST/JWT.
- **Pendiente F2.B**: columna/índice pgvector persistente entre consultas (requiere ML stack corriendo, `requirements-ml.txt` + overlay pgvector).
- Luego F2.C (auth/Alembic/RUT/empresas) o F2.D (UI/PDF/observabilidad).
- ⚠️ `.gitignore` local mantiene `/docs` — nuevos docs con `git add -f`.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): ✅ **cerrado** — código `T-22`/`T-46`/`T-102`/`T-103`/`T-104`/`T-105` + legal `T-100`/`T-101`
- Fase 2: 🟡 **F2.A** código + infra de validación (`T-201/202/204`; live pendiente `T-200/203/205`) · **F2.B** `T-210`/`T-212` ✅, `T-211` embeddings+overlay ✅ (store pgvector persistente pendiente) · F2.C/D no iniciadas

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.
- `T-104`/`T-65`/`T-66` se difieren para acompañar el scraper real (Fase 2), donde tienen efecto real.

## Últimas tareas completadas
- `T-210`/`T-211`/`T-212` **Fase 2 F2.B**: síntesis NLP en el informe, `embeddings_service` (mock+skeleton), endpoint `/similar` y overlay pgvector (+11 tests)
- **Fix Docker** WSL: `credsStore: desktop.exe` roto removido de `~/.docker/config.json`
- **Infra de validación en vivo**: overlay `docker-compose.live.yml` (worker+Chromium), `scripts/inspect_ojv.py`/`validate_live.py` + runbook; `job_timeout` arq (T-65 parcial)
- `T-201`/`T-202`/`T-204` **Fase 2 F2.A**: scraper real abre modal de detalle, parsea litigantes/relaciones por sufijo, robustez (retry/user-agent) (+6 tests)
- `T-100`/`T-101` **revisión legal cerrada** (decisiones del responsable, `ff8b8c0`)
- `T-104` **politeness/rate limiting** (`RateLimiter` + `retry_async`, `6126ff2`)
- `T-102`/`T-105` **compliance M10**: API key + `motivo` endurecido y evidencia de propósito (`043d6ec`)

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
