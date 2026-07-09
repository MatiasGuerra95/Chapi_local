# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**M10 cerrado** y **Fase 2 F2.A (scraper real, código) implementada.** En `origin/main`: hardening/compliance (`3ada43b`, `043d6ec`, `6126ff2`), compliance docs (`6b508d3`), cierre legal (`ff8b8c0`). `PlaywrightPjudScraper` ya abre el modal de detalle y puebla litigantes/relaciones por sufijo de competencia; robustez con `retry_async`/user-agent/politeness. Verificado: ruff ✅ + import ✅ + pytest **40 passed / 1 skipped**. Falta commitear el código de F2.A.

## Ahora / próximo
- **Commitear/pushear** F2.A (scraper + parsers + tests).
- **Requiere sitio en vivo (tú, entorno controlado):** `T-200` verificar values Civil/Cobranza y sufijos del modal, `T-203` detalle vía POST/JWT si aplica, `T-205` activar `USE_MOCK_SCRAPER=false` y validar E2E con Playwright (instalar chromium: `INSTALL_BROWSERS=true`).
- Luego F2.B (LLM/pgvector) o F2.C/D según prioridad.
- ⚠️ `.gitignore` local mantiene `/docs` — nuevos docs con `git add -f`.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): ✅ **cerrado** — código `T-22`/`T-46`/`T-102`/`T-103`/`T-104`/`T-105` + legal `T-100`/`T-101`
- Fase 2: 🟡 **F2.A código listo** (`T-201`/`T-202`/`T-204`); pendiente validación en vivo (`T-200`/`T-203`/`T-205`); F2.B/C/D no iniciadas

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.
- `T-104`/`T-65`/`T-66` se difieren para acompañar el scraper real (Fase 2), donde tienen efecto real.

## Últimas tareas completadas
- `T-201`/`T-202`/`T-204` **Fase 2 F2.A**: scraper real abre modal de detalle, parsea litigantes/relaciones por sufijo, robustez (retry/user-agent) (+6 tests)
- `T-100`/`T-101` **revisión legal cerrada** (decisiones del responsable, `ff8b8c0`)
- `T-104` **politeness/rate limiting** (`RateLimiter` + `retry_async`, `6126ff2`)
- `T-102`/`T-105` **compliance M10**: API key + `motivo` endurecido y evidencia de propósito (`043d6ec`)

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
