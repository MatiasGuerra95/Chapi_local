# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**MVP mergeado a `main`**; avanzando el frente **M10 (hardening)**. Commiteado `3ada43b`: `T-22` índices, `T-46` readiness `GET /health/ready`, `T-103` logging JSON con correlación. En árbol de trabajo (por commitear): `T-102` control de acceso por API key + `T-105` motivo endurecido + evidencia de propósito en auditoría. Verificado: ruff ✅ + import ✅ + pytest **29 passed / 1 skipped** (integración se salta sin Postgres).

## Ahora / próximo
- **Commitear** T-102/T-105 a `main` (directo).
- Seguir M10: `T-103`✅/`T-104` (rate limiting → se difiere al scraper real). Quedan `T-100`/`T-101` (legal/retención, decisión del usuario) y transversales `T-104` (Fase 2).
- ⚠️ `.gitignore` local agrega `/docs` (ignoraría la carpeta de documentación) — **revisar/revertir** (no commiteado).

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): 🟡 en curso — `T-22`/`T-46`/`T-103`/`T-102`/`T-105` ✅; legal (`T-100`/`T-101`) pendiente; `T-104` diferido
- Fase 2: ⬜ no iniciada

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.
- `T-104`/`T-65`/`T-66` se difieren para acompañar el scraper real (Fase 2), donde tienen efecto real.

## Últimas tareas completadas
- `T-102`/`T-105` **compliance M10**: control de acceso por API key + `motivo` endurecido y evidencia de propósito en auditoría (+11 tests)
- `T-22`/`T-46`/`T-103` **hardening M10**: índices de BD, readiness DB+Redis, logging JSON con correlación (commit `3ada43b`)
- `T-94` **merge del PR #1 a main** (squash `de7cb59`); rama eliminada

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
