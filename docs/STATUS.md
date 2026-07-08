# STATUS — Chapi Local

_Última actualización: 2026-07-08 · rama `feat/mvp-due-diligence-compliance` (PR #1)_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
Núcleo del MVP **implementado** (API + worker + servicios + infra + tests unitarios) y subido en el **PR #1**.
Falta cerrar el MVP: versionar la documentación, verificación end-to-end con Docker, tests de integración y merge.

## Ahora / próximo
- **Siguiente:** `T-04/T-93` versionar `docs/` + `CLAUDE.md` en el repo → `T-85` verificación E2E con `docker compose`.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟡 unitarias ✅ · integración/E2E pendientes
- Entrega (M9): 🟡 PR #1 abierto · falta CI verde + merge
- Compliance operativo (M10): ⬜ pendiente
- Fase 2: ⬜ no iniciada

## Bloqueos / decisiones abiertas
- ⛔ `T-85` bloqueado: daemon de Docker caído; sin Postgres/Redis locales.
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.

## Últimas tareas completadas
- `T-06/T-07` sistema de seguimiento (STATUS + memoria) + `CLAUDE.md` con *Session workflow*
- `T-01/T-02/T-03` documentación (requirements · plan · tasks)
- `T-90/T-91` rama + commit + push + PR #1

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
