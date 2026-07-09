# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**MVP en `main`**; frente **M10 casi cerrado**. Pusheado a `origin/main`: `T-22`/`T-46`/`T-103` (`3ada43b`), `T-102`/`T-105` (`043d6ec`), `T-104` politeness/throttle (`6126ff2`). Redactados (borradores) `T-100` y `T-101` en `docs/compliance/`. Verificado: ruff ✅ + import ✅ + pytest **34 passed / 1 skipped**.

## Ahora / próximo
- **Commitear** los docs de compliance (T-100/T-101) — ojo: `.gitignore` local ignora `/docs`, así que se agregan con `git add -f`.
- M10 sólo queda a la espera de **decisiones legales/negocio**: validar `T-100` (base de licitud + ToS OJV) y `T-101` (plazos de retención, auditoría vs. supresión). Ver los `⚠️ DECISIÓN REQUERIDA` en los borradores.
- Con M10 cerrado → **Fase 2** (scraper real: `T-200` competencias Civil/Cobranza, `T-201` PlaywrightPjudScraper), **gated** por T-100.
- ⚠️ `.gitignore` local mantiene `/docs` (por decisión del usuario) — nuevos docs requieren `git add -f`.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): 🟡 casi — código `T-22`/`T-46`/`T-102`/`T-103`/`T-104`/`T-105` ✅; `T-100`/`T-101` borrador redactado, **pendiente validación legal**
- Fase 2: ⬜ no iniciada (gated por T-100)

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
