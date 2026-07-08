# STATUS — Chapi Local

_Última actualización: 2026-07-08 · rama `main` · PR #1 mergeado (squash `de7cb59`)_

> Marcador de sesión. Responde "¿dónde nos quedamos?" en una pantalla.
> Backlog completo con checkboxes en [`tasks.md`](./tasks.md).

## ¿Dónde nos quedamos?
**MVP completo y mergeado a `main`** (PR #1, squash `de7cb59`): API + worker + Postgres + Redis, verificado E2E (app-level + smoke docker) con CI en verde. Toca decidir el siguiente frente: compliance operativo (M10) o Fase 2 (scraper real).

## Ahora / próximo
- **Elegir frente:** M10 compliance operativo (`T-100` legal/ToS PJUD, `T-101` retención de datos) **o** Fase 2 (`T-200/T-201` scraper real Playwright).
- Rápidos opcionales: `T-86` script demo · `T-23` decidir JSON por-persona vs por-consulta.

## Progreso (detalle en tasks.md)
- Código MVP (M1–M7): ✅ hecho
- Pruebas (M8): 🟢 unit + integración (pytest+Postgres) ✅ · E2E app-level ✅ · smoke full-stack docker ✅ (16 tests)
- Entrega (M9): 🟢 **mergeado a main** (squash `de7cb59`)
- Compliance operativo (M10): ⬜ pendiente
- Fase 2: ⬜ no iniciada

## Bloqueos / decisiones abiertas
- ⚠️ `T-23` colisión del JSON por persona · `T-100` revisión legal ToS PJUD · `T-101` retención de datos.

## Últimas tareas completadas
- `T-94` **merge del PR #1 a main** (squash `de7cb59`); rama eliminada
- `T-92` CI del PR en verde (ruff + import + unit/integración con Postgres)
- `T-83/T-84/T-87` tests pytest de integración (API+worker+Postgres) e informe; CI con servicio Postgres

---
_Mantenimiento: al completar una tarea → (1) marcar su checkbox en `tasks.md`,
(2) actualizar aquí «Última actualización», «Ahora/próximo» y «Últimas tareas completadas».
Mantener ≤1 pantalla; no duplicar el backlog._
