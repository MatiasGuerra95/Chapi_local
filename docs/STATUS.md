# STATUS — Chapi Local

_Última actualización: 2026-07-08 · rama `feat/mvp-due-diligence-compliance` (PR #1)_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
Núcleo del MVP **implementado** (API + worker + servicios + infra + tests unitarios) y subido en el **PR #1**.
Falta cerrar el MVP: versionar la documentación, verificación end-to-end con Docker, tests de integración y merge.

## Ahora / próximo
- **Siguiente:** `T-94` revisión + **merge** del PR #1 (pendiente de tu OK).

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅ (16 tests)
- Entrega (M9): 🟡 PR #1 con **CI verde** · falta merge (T-94)
- Compliance operativo (M10): ⬜ pendiente
- Fase 2: ⬜ no iniciada

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.

## Últimas tareas completadas
- `T-92` CI del PR en verde (ruff + import + unit/integración con Postgres)
- `T-83/T-84/T-87` tests pytest de integración (API+worker+Postgres) e informe; CI con servicio Postgres
- `T-88` smoke full-stack docker (CA-06) ✅ — corrigió carrera `create_all` (db.py) y Dockerfile trixie; Chromium opt-in (T-73)

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
