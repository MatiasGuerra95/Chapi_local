# STATUS — Chapi Local

_Última actualización: 2026-07-09 · rama `main` · MVP mergeado (squash `de7cb59`) + hardening M10 en curso_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**MVP mergeado a `main`**; arrancó el frente **M10 (hardening de código)**. Hechos hoy: `T-22` índices, `T-46` readiness `GET /health/ready`, `T-103` logging JSON con correlación (request-id/job-id). Verificado: ruff ✅ + import ✅ + pytest **18 passed / 1 skipped** (integración se salta sin Postgres). **Sin commitear aún** (en árbol de trabajo).

## Ahora / próximo
- **Commitear** el hardening (T-22/T-46/T-103) — ¿rama + PR o directo?
- Seguir M10 hardening: `T-104` rate limiting/politeness → **se difiere para acompañar el scraper real** (no hay llamadas HTTP que throttlear en el mock); `T-102` control de acceso, `T-105` refuerzo de propósito.
- Pendiente de decisión del usuario: `T-100` legal/ToS PJUD, `T-101` retención de datos.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): 🟡 en curso — hardening `T-22`/`T-46`/`T-103` ✅; legal (`T-100`/`T-101`) pendiente
- Fase 2: ⬜ no iniciada

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.
- `T-104`/`T-65`/`T-66` se difieren para acompañar el scraper real (Fase 2), donde tienen efecto real.

## Últimas tareas completadas
- `T-22`/`T-46`/`T-103` **hardening M10**: índices de BD, readiness DB+Redis, logging JSON con correlación (+3 tests `test_health.py`)
- `T-94` **merge del PR #1 a main** (squash `de7cb59`); rama eliminada
- `T-92` CI del PR en verde (ruff + import + unit/integración con Postgres)

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
