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
- [x] **T-22** Índices para acceso frecuente: `case_results.consulta_id`, `consultas.created_at`, `audit_logs.consulta_id` (`index=True` en modelos; se crean vía `create_all`) (rendimiento).
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
- [x] **T-46** Readiness check `GET /health/ready` que verifica DB (`SELECT 1`) y Redis (`arq_pool.ping()`): 200 si ambos ok, 503 con detalle por componente (RNF-07).

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
- [ ] **T-65** `job_timeout` de arq **hecho** (`ARQ_JOB_TIMEOUT_SECONDS`, default 1800 s, en `WorkerSettings`); falta afinar la política de **reintentos** (`max_tries`) acorde a politeness (RNF-03). ⚠️
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
- [x] **T-92** CI en verde sobre el PR (build **pass**: ruff + import + unit/integración con servicio Postgres).
- [x] **T-93** Incluir la documentación (`requirements`/`plan`/`tasks`/`STATUS`) y `CLAUDE.md` en el PR (commit `6b7d63b`).
- [x] **T-94** Merge a `main` (squash, commit `de7cb59`); rama `feat/...` eliminada (local y remota).

## M10 · Compliance operativo y endurecimiento (transversal)
- [x] **T-100** Revisión legal **cerrada** (decisiones del responsable, 2026-07-09): base = consentimiento + interés legítimo; ToS de la OJV **permiten** consulta automatizada; causas penales con revisión humana. Gate de Fase 2 **levantado**. *(`docs/compliance/legal-basis-and-tos.md`)*
- [x] **T-101** Política de **retención y eliminación** **aprobada**: plazos (6 meses no contratados; contratados = relación + plazo legal), auditoría append-only con seudonimización al vencer. Falta (no bloqueante) el enforcement técnico (`RETENTION_DAYS` + purga). *(`docs/compliance/data-retention-policy.md`)*
- [x] **T-102** Control de acceso mínimo por API key (activable con `API_KEY`; abierto en dev/MVP) en endpoints de negocio (consultas/audit); health/readiness abiertos. Minimización: las respuestas no exponen rutas de FS ni secretos. Auth por usuario/RBAC → fase 2 (T-220). *(`app/security.py`)*
- [x] **T-103** Logging estructurado JSON con correlación (`request_id` en API vía middleware + header `X-Request-ID`; `job_id` de arq en el worker) para trazabilidad técnica. *(`app/logging_config.py`)*
- [x] **T-104** Politeness/rate limiting hacia la fuente: `RateLimiter` (intervalo mínimo + jitter) y `retry_async` (backoff exponencial) en `app/services/throttle.py`, configurables (`SCRAPER_*`) y cableados en el skeleton Playwright (antes de cada búsqueda). Efectivo al activar el scraper real (fase 2).
- [x] **T-105** Reforzar evidencia de propósito: validación de `motivo` endurecida (rechaza triviales/repetitivos/símbolos/una-palabra, no sólo por longitud) + auditoría de `consulta_creada` enriquecida con `principal` y `request_id` (RC-01, RC-05).

---

## Fase 2 🔒

### F2.A · Scraper real (Playwright)
- [ ] 🔒 **T-200** Verificar los `value` de competencia **Civil** y **Cobranza** en `#nomCompetencia` y los **sufijos** de tabla del modal (`Civ`/`Cob`) (DOM vivo) (RNF-08). ⚠️ requiere sitio en vivo.
- [x] 🔒 **T-201** TODO de `PlaywrightPjudScraper` implementados: user-agent, apertura del modal de detalle por fila (`a.toggle-modal` → `.modal.show`) y poblado de litigantes/relaciones.
- [x] 🔒 **T-202** Parseo de `litigantes`/`relaciones` por competencia con selectores por sufijo (`COMPETENCIA_SUFIJO`; Pen/Lab confirmados) + tests (`tests/test_pjud_parsers.py`).
- [ ] 🔒 **T-203** Manejo de sesión/JWT para el detalle vía POST (referencia `detalle.py`). El path por modal (`toggle-modal`) no lo requiere; pendiente sólo si algún detalle exige POST con token. ⚠️ requiere sitio en vivo.
- [x] 🔒 **T-204** Robustez: `retry_async` (backoff) en la búsqueda, user-agent configurable, apertura de detalle tolerante a fallos, politeness (T-104). Tolerancia a cambios de DOM: pendiente afinar con el sitio vivo.
- [ ] 🔒 **T-205** Activar por config (`USE_MOCK_SCRAPER=false`) y validar contra un entorno de prueba. **Infra lista**: overlay `docker-compose.live.yml` (worker con Chromium), `scripts/inspect_ojv.py` (T-200), `scripts/validate_live.py` y runbook `scripts/README-live-validation.md`. Chromium con `--no-sandbox`, `job_timeout` subido. ⚠️ falta la corrida en vivo (la ejecutas tú).

### F2.B · LLM y búsqueda semántica
- [x] 🔒 **T-210** `nlp_service` con síntesis narrativa: `MockSummarizer` rule-based (default MVP, compliant RC-03) + skeleton `LlamaCppSummarizer` (lazy, opt-in `USE_MOCK_NLP=false`); cableado en el informe (+6 tests). Reemplaza el stub inicial.
- [ ] 🔒 **T-211** Embeddings + pgvector: `embeddings_service` (`MockEmbedder` hashing + skeleton `SentenceTransformerEmbedder`) ✅ y overlay `docker-compose.pgvector.yml` (imagen `pgvector/pgvector:pg16` + init SQL) ✅. **Pendiente**: columna/índice pgvector persistente entre consultas (requiere ML stack corriendo). ⚠️
- [x] 🔒 **T-212** Endpoint `GET /consultas/{id}/similar?q=&top=`: ranking por similitud coseno de embeddings sobre las causas de la consulta (en memoria; gated por `ENABLE_SEMANTIC_SEARCH`) + tests (`tests/test_embeddings.py`).

### F2.C · Identidad, datos y migraciones
- [x] 🔒 **T-220** Auth de usuarios internos (reemplaza DD-05): modelo `User`, hashing pbkdf2 (stdlib) + JWT (PyJWT), router `/auth` (token/me/users con RBAC admin), gate unificado `authorize` (JWT si `AUTH_ENABLED`, si no API key de T-102), `scripts/create_user.py` y migración Alembic `b7decc69951e`. Verificado E2E contra Postgres real (+8 unit, +1 integración).
- [x] 🔒 **T-221** Migraciones con **Alembic** (async env.py + `alembic.ini` + migración inicial `6cb55646f788`). `create_all` sigue de default en dev/tests; en prod `AUTO_CREATE_TABLES=false` + `alembic upgrade head`. Verificado: autogenerate + upgrade/downgrade round-trip contra Postgres real.
- [ ] 🔒 **T-222** **Desambiguación de homónimos por RUT hecha** (RC-04): `rut_utils` normaliza RUT y, si el sujeto tiene RUT y una causa lo lista entre sus litigantes, el worker desmarca `possible_homonym` (+7 tests). **Pendiente**: consulta por RUT como *input* de búsqueda (flujo distinto en la OJV).
- [x] 🔒 **T-223** Consulta de **empresas** (RD-01): `SubjectIn` valida por tipo (persona requiere nombre; empresa requiere `razon_social`, que se enruta a `nombre` para la búsqueda). Verificado E2E con mock (consulta empresa → `done` + informe con razón social). Nota: el flujo real por razón social en la OJV se confirma junto a T-200/T-205.

### F2.D · Producto y operación
- [x] 🔒 **T-230** UI mínima server-rendered (Jinja2): `GET /ui` (form + consultas recientes), `POST /ui/consultas` (reutiliza `consulta_service` → motivo+auditoría), `GET /ui/consultas/{id}` (estado con auto-refresh + enlace al informe). Verificada E2E contra Postgres real.
- [ ] 🔒 **T-231** Exportar informe a **PDF**.
- [x] 🔒 **T-232** Observabilidad: endpoint `GET /metrics` (Prometheus) con contadores de requests HTTP (método/ruta/status + duración, vía middleware) y gauges de negocio (consultas por estado, causas totales) calculados desde la BD. Dashboards/alertas quedan al stack externo (Prometheus/Grafana). *(`app/metrics.py`)*
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
