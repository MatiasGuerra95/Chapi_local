# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**M10 cerrado.** Pusheado a `origin/main`: hardening + compliance (`3ada43b`, `043d6ec`, `6126ff2`) y compliance docs (`6b508d3`). **T-100/T-101 cerradas** (decisiones del responsable 2026-07-09: base consentimiento+interés legítimo; ToS OJV **permiten** scraping; penales con revisión humana; retención aprobada). **Gate de Fase 2 levantado.** Arrancando **Fase 2 (scraper real, código)**.

## Ahora / próximo
- **Fase 2 F2.A (código):** `T-201` implementar PlaywrightPjudScraper, `T-202` parseo litigantes/relaciones, `T-204` robustez (usa `throttle.py`). Tests de parsers con HTML de ejemplo (sin navegador).
- **Requiere sitio en vivo (tú, entorno controlado):** `T-200` verificar values Civil/Cobranza en `#nomCompetencia`, `T-203` sesión/JWT del detalle, `T-205` activar `USE_MOCK_SCRAPER=false` y validar.
- ⚠️ `.gitignore` local mantiene `/docs` (decisión del usuario) — nuevos docs con `git add -f`.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): ✅ **cerrado** — código `T-22`/`T-46`/`T-102`/`T-103`/`T-104`/`T-105` + legal `T-100`/`T-101`
- Fase 2: 🟡 **iniciada** (F2.A scraper real, código); ejecución en vivo pendiente (T-200/T-205)

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.
- `T-104`/`T-65`/`T-66` se difieren para acompañar el scraper real (Fase 2), donde tienen efecto real.

## Últimas tareas completadas
- `T-100`/`T-101` **borradores de compliance** en `docs/compliance/` (base de licitud/ToS + retención), pendientes de validación legal
- `T-104` **politeness/rate limiting** (`RateLimiter` + `retry_async`, `6126ff2`, +5 tests)
- `T-102`/`T-105` **compliance M10**: API key + `motivo` endurecido y evidencia de propósito (`043d6ec`, +11 tests)
- `T-22`/`T-46`/`T-103` **hardening M10**: índices, readiness, logging con correlación (`3ada43b`)

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
