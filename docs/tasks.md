# Tareas — Chapi Local

> Desglose de tareas basado en [`requirements.md`](./requirements.md) y
> [`plan.md`](./plan.md). Organizado por hitos (milestones) en orden lógico de
> construcción. Cada tarea referencia los IDs de requisito/criterio que satisface.

## Leyenda
- `[x]` **Hecho** — implementado y commiteado en la rama `feat/mvp-due-diligence-compliance` (PR #1).
- `[ ]` **Pendiente** — por hacer.
- ⚠️ **Decisión/riesgo** — requiere una definición antes o durante la ejecución (ver §Decisiones abiertas).
- 🔒 **Fase 2** — fuera del MVP.

## Estado (snapshot)
- **Núcleo del MVP (código): implementado.** API, worker, servicios, modelos, infra y tests unitarios están construidos.
- **Falta para "MVP terminado":** verificación end‑to‑end con Postgres+Redis reales, tests de integración, versionar la documentación y merge del PR.
- **Bloqueo conocido en el entorno de desarrollo:** el daemon de Docker está caído y no hay Postgres/Redis locales → T-85 pendiente de ejecutar.

---

## M0 · Planificación y documentación
- [x] **T-00** Plan inicial y decisiones (estructura `backend/app`, arq, diferir LLM/pgvector).
- [x] **T-01** Redactar `docs/requirements.md` (requisitos con IDs).
- [x] **T-02** Redactar `docs/plan.md` (arquitectura, flujo, decisiones).
- [x] **T-03** Redactar `docs/tasks.md` (este documento).
- [x] **T-06** Sistema de seguimiento: `docs/STATUS.md` + memoria persistente (índice `MEMORY.md`).
- [x] **T-07** `CLAUDE.md` (guía del repo + *Session workflow* que alinea STATUS/tasks).
- [x] **T-04** Versionar `docs/` y `CLAUDE.md` en el repositorio (commit `6b7d63b`, PR #1).
- [ ] **T-05** Validar requisitos con stakeholders (RRHH + legal) y obtener sign-off. ⚠️

## M1 · Fundaciones (estructura, configuración, base de datos)
- [x] **T-10** Reestructurar a `backend/app/` + `workers/` (DD-01, RNF-05).
- [x] **T-11** `config.py` con pydantic-settings + mapa `COMPETENCIAS` (RNF-06).
- [x] **T-12** `db.py`: engine async, sessionmaker, `Base`, `init_models()` (RNF-02, DD-06).
- [x] **T-13** `.env.sample` + `.gitignore` (excluir `.env`/secretos) (RC-08, RNF-06).

## M2 · Dominio y persistencia
- [x] **T-20** Modelos SQLAlchemy: `Subject`, `Consulta`, `CaseResult`, `AuditLog`, `Report` (RD-01…RD-05).
- [x] **T-21** JSONB para `params`/`litigantes`/`relaciones` (RD-06).
- [ ] **T-22** Índices para acceso frecuente: `case_results.consulta_id`, `consultas.created_at`, `audit_logs.consulta_id` (rendimiento).
- [ ] **T-23** Resolver colisión del JSON por persona: `results/{slug}.json` se **sobrescribe** al re-consultar a la misma persona → decidir namespacing por `consulta_id`/timestamp o versionado (RF-05, RNF-10). ⚠️

## M3 · Schemas y validación (compliance de entrada)
- [x] **T-30** Schemas Pydantic (Subject/Consulta/CaseResult/Audit; in/out).
- [x] **T-31** Gating de `motivo` obligatorio y no trivial (RC-01, RC-02).
- [x] **T-32** Validar competencias soportadas y rango de años (RF-02).
- [ ] **T-33** Normalizar entrada de nombre/apellidos (mayúsculas/acentos) para el scraper real (RNF-08).

## M4 · API (routers)
- [x] **T-40** `GET /health` (RF-13).
- [x] **T-41** `POST /consultas`: crea sujeto+consulta, audita, encola (RF-01, RF-03, RF-11).
- [x] **T-42** `GET /consultas` y `GET /consultas/{id}` con causas/conteos (RF-09, RF-10).
- [x] **T-43** `GET /consultas/{id}/report` (HTML) (RF-08).
- [x] **T-44** `GET /audit` con filtro por consulta (RF-12).
- [ ] **T-45** Paginación/límite en listados de consultas y auditoría (escalabilidad).
- [ ] **T-46** Readiness check que verifique conectividad a DB y Redis (además del liveness) (RNF-07).

## M5 · Servicios
- [x] **T-50** Interfaz `PjudScraper` (Protocol) + factory `get_scraper()` (RF-14, DD-04).
- [x] **T-51** `MockPjudScraper` con homónimos demostrativos (RC-04).
- [x] **T-52** Skeleton `PlaywrightPjudScraper` portado de `crawler_nom.py` (RNF-08).
- [x] **T-53** `risk_engine` rule-based, sin culpabilidad/recomendación (RF-07, RC-03).
- [x] **T-54** `report_generator` + `report.html.j2` con disclaimer (RF-08, RC-06).
- [x] **T-55** `audit_service` append-only (RF-11, RC-05, RC-07).

## M6 · Worker y cola
- [x] **T-60** `arq WorkerSettings` + `run_consulta()` (RF-03…RF-08).
- [x] **T-61** Escritura de JSON en tiempo real por persona (RF-05, RNF-10).
- [x] **T-62** Persistencia normalizada de causas (RF-06).
- [x] **T-63** Cálculo de score y cierre de la consulta (RF-07).
- [x] **T-64** Manejo de errores → estado `error` + auditoría (RNF-07).
- [ ] **T-65** Configurar `job_timeout` y reintentos de arq (el scraper real es lento: espera hasta ~45 s por tabla) (RNF-03). ⚠️
- [ ] **T-66** Commit incremental/por lotes de `CaseResult` (hoy es una transacción única para todo el scrape; con el scraper real será enorme y de larga duración) (RF-06). ⚠️

## M7 · Infraestructura
- [x] **T-70** `docker-compose.yml` (api, worker, db, redis) con health checks (RNF-04).
- [x] **T-71** `infra/Dockerfile` (imagen compartida api/worker + Playwright chromium).
- [x] **T-72** `requirements.txt` (MVP) + `requirements-ml.txt` (fase 2) (DD-03).
- [x] **T-73** Imagen sin Chromium por defecto: instalación opt-in con `--build-arg INSTALL_BROWSERS=true` (fase 2). *(infra/Dockerfile)*
- [ ] **T-74** Definir persistencia/backup de Postgres y ciclo del volumen `dbdata` (operación).

## M8 · Calidad, pruebas y verificación E2E
- [x] **T-80** Lint `ruff` en CI (RNF-09).
- [x] **T-81** Tests unitarios: `risk_engine`, `MockPjudScraper`, `schemas` (CA-02, parte de CA-04).
- [x] **T-82** CI: `ruff` + import de `app.main` + `pytest`.
- [x] **T-83** Tests de integración API+worker (`httpx.ASGITransport`) contra Postgres real (`tests/test_integration.py`); CI los corre con un servicio Postgres. Se saltan sin `DATABASE_URL`.
- [x] **T-84** Cobertura de `run_consulta` incluida en el test de integración (worker invocado directamente, sin Redis).
- [x] **T-85** **Verificación E2E app-level** contra **Postgres local** (mock scraper + worker directo, sin Redis): 422 sin motivo, `done` con causas/score, JSON en tiempo real, informe con disclaimer/homónimos, auditoría completa (CA-01/02/03/04/05 · RC-03/RC-04). *(script: `scratchpad/verify_e2e.py`)*
- [x] **T-88** Smoke del **stack completo** con `docker compose` (API+worker+Postgres+Redis): CA-06 ✅ + cola real Redis/arq + CA-01..05/RC-04. *(script: `scratchpad/smoke_docker.py`)* Detectó y corrigió: carrera de `create_all` API↔worker (`db.py`) y Dockerfile en Debian trixie (`libgl1-mesa-glx`→`libgl1`).
- [ ] **T-86** Script de smoke test / demo (crear consulta → esperar `done` → abrir informe).
- [x] **T-87** Test RC-03/RC-04 del informe (`tests/test_report.py`): indicadores sin lenguaje prohibido + disclaimer que lo niega + marca de homónimo. (Confirmado: no basta "ausencia de palabras"; el disclaimer las menciona para negarlas.)

## M9 · Entrega
- [x] **T-90** Rama `feat/mvp-due-diligence-compliance` + commit del MVP.
- [x] **T-91** Push + PR [#1](https://github.com/MatiasGuerra95/Chapi_local/pull/1).
- [ ] **T-92** CI en verde sobre el PR.
- [x] **T-93** Incluir la documentación (`requirements`/`plan`/`tasks`/`STATUS`) y `CLAUDE.md` en el PR (commit `6b7d63b`).
- [ ] **T-94** Revisión de código y **merge** a `main`.

## M10 · Compliance operativo y endurecimiento (transversal)
- [ ] **T-100** Revisión legal: base de licitud del tratamiento y **Términos de Uso** de la OJV/PJUD para scraping automatizado (RC-05). ⚠️
- [ ] **T-101** Política de **retención y eliminación** de datos personales (Ley 19.628 / Ley 21.719): plazos, borrado, propósito limitado.
- [ ] **T-102** Control de acceso y minimización: quién puede crear consultas y ver resultados/informes.
- [ ] **T-103** Logging estructurado con correlación (request id / job id) para trazabilidad técnica.
- [ ] **T-104** Rate limiting y "politeness" hacia la fuente (throttling/backoff) — prerequisito del scraper real.
- [ ] **T-105** Reforzar registro de propósito por consulta (evidencia de finalidad legítima) (RC-01, RC-05).

---

## Fase 2 🔒

### F2.A · Scraper real (Playwright)
- [ ] 🔒 **T-200** Verificar los `value` de competencia **Civil** y **Cobranza** en `#nomCompetencia` (DOM vivo) (RNF-08).
- [ ] 🔒 **T-201** Implementar los TODO de `PlaywrightPjudScraper` (navegación completa + apertura de modales de detalle).
- [ ] 🔒 **T-202** Parseo de `litigantes`/`relaciones` por competencia (selectores por sufijo).
- [ ] 🔒 **T-203** Manejo de sesión/JWT para el detalle (referencia `detalle.py`).
- [ ] 🔒 **T-204** Robustez: esperas, reintentos, rotación de user-agent, tolerancia a cambios de DOM.
- [ ] 🔒 **T-205** Activar por config (`USE_MOCK_SCRAPER=false`) y validar contra un entorno de prueba.

### F2.B · LLM y búsqueda semántica
- [ ] 🔒 **T-210** Integrar resumen de fallos con llama-cpp en `nlp_service` (instalar `requirements-ml.txt`).
- [ ] 🔒 **T-211** Embeddings + pgvector — requiere **imagen Postgres con la extensión pgvector** (postgres:16 no la trae). ⚠️
- [ ] 🔒 **T-212** Endpoint/consulta semántica sobre causas.

### F2.C · Identidad, datos y migraciones
- [ ] 🔒 **T-220** Autenticación/autorización de usuarios internos (reemplaza DD-05).
- [ ] 🔒 **T-221** Migraciones con **Alembic** (reemplaza `create_all`, DD-06).
- [ ] 🔒 **T-222** Consulta por **RUT** y desambiguación de homónimos por RUT (RC-04).
- [ ] 🔒 **T-223** Consulta de **empresas** (razón social/RUT) (RD-01).

### F2.D · Producto y operación
- [ ] 🔒 **T-230** UI mínima para reclutadores (crear consulta, ver estado/informe).
- [ ] 🔒 **T-231** Exportar informe a **PDF**.
- [ ] 🔒 **T-232** Observabilidad (métricas, dashboards, alertas).
- [ ] 🔒 **T-233** Evaluar fuentes adicionales (Boletín Comercial, inhabilidades, etc.).

---

## Decisiones abiertas (bloquean o condicionan tareas)
1. **JSON por persona vs por consulta** (T-23): ¿se acepta la sobrescritura de `results/{slug}.json` o se versiona por consulta? Afecta RF-05/RNF-10.
2. **Legalidad del scraping** (T-100): confirmar base de licitud y ToS del PJUD antes de activar el scraper real (T-200+).
3. **Retención de datos** (T-101): definir plazos de conservación/borrado de datos personales.
4. **Transaccionalidad del worker** (T-66) y **timeouts** (T-65): estrategia para scrapes largos del scraper real.
5. **Alcance de la verificación E2E** (T-85): ¿se ejecuta localmente (requiere levantar Docker) o en CI con servicios de Postgres/Redis?

## Sugerencia de orden (próximos pasos del MVP)
1. **T-04/T-93** versionar docs → 2. **T-85** verificación E2E (levantar Docker) → 3. **T-83/T-84/T-87** tests de integración → 4. **T-92/T-94** CI verde + merge → 5. luego M10 (compliance operativo) antes de abrir Fase 2.
