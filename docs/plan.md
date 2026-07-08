# Plan de construcción — Chapi Local

> Este documento describe **cómo** estamos construyendo el sistema (arquitectura,
> componentes, flujo y decisiones técnicas), sobre la base de
> [`requirements.md`](./requirements.md). No incluye la lista de tareas (se define
> más adelante). Las referencias `RF-/RD-/RC-/RNF-/DD-` apuntan a ese documento.

## 1. Enfoque general

Construimos un **MVP funcional de extremo a extremo** con la lógica de negocio real
(persistencia, auditoría, score, informe) pero con el scraping **mockeado** detrás de
una **interfaz reemplazable** (DD-04, RF-14). Así validamos el flujo completo sin
depender del sitio del Poder Judicial, y el paso a Playwright real (fase 2) no toca
la API ni el worker: solo cambia una implementación y un flag de configuración.

Principios:
- **Async de punta a punta** (FastAPI + SQLAlchemy async + arq), coherente con Playwright async.
- **Separación de responsabilidades**: la API orquesta y responde; el **worker** hace el
  trabajo pesado; los **servicios** encapsulan scraping, score, informe y auditoría.
- **Compliance por diseño**: el motivo obligatorio, la auditoría y el disclaimer no son
  añadidos opcionales, sino puntos de control en el flujo (sección 8).

## 2. Arquitectura (visión de componentes)

```
                    ┌───────────────────────────────────────────────┐
   Cliente  ──HTTP──▶            API (FastAPI, async)                 │
 (curl/UI)          │  routers: health · consultas · audit           │
                    │  - valida (schemas) · audita · encola trabajo   │
                    └───────┬───────────────────────┬────────────────┘
                            │ enqueue (arq)          │ lee/escribe
                            ▼                         ▼
                    ┌──────────────┐        ┌────────────────────┐
                    │  Redis (cola)│        │  PostgreSQL (async) │
                    └──────┬───────┘        │  subjects/consultas │
                           │ job            │  case_results       │
                           ▼                │  audit_logs/reports │
                 ┌───────────────────────┐ └─────────▲──────────┘
                 │  Worker (arq)         │           │ persiste + audita
                 │  run_consulta()       │───────────┘
                 │  - get_scraper()      │
                 │  - JSON en tiempo real│──▶ results/{persona}.json
                 │  - risk_engine        │
                 └──────────┬────────────┘
                            │ usa
                            ▼
                 ┌───────────────────────────────────────────┐
                 │ services/                                   │
                 │  pjud_scraper (Protocol + Mock + Playwright)│
                 │  risk_engine · report_generator · audit     │
                 └───────────────────────────────────────────┘
```

## 3. Estructura del proyecto (RNF-05)

```
backend/app/
  main.py          # FastAPI + lifespan (crea tablas y pool arq)
  config.py        # Settings (pydantic-settings) + mapa de competencias
  db.py            # engine async + sessionmaker + Base + init_models()
  models.py        # SQLAlchemy 2.0 (Subject, Consulta, CaseResult, AuditLog, Report)
  schemas.py       # Pydantic v2 (validación + serialización)
  routers/         # health · consultas · audit
  services/        # pjud_scraper · risk_engine · report_generator · audit_service
  templates/       # report.html.j2
workers/
  judicial_worker.py   # arq WorkerSettings + run_consulta()
infra/Dockerfile · docker-compose.yml · requirements*.txt · .env.sample
tests/  ·  docs/  ·  results/
```

## 4. Componentes y responsabilidades

### 4.1 API (FastAPI)
- Recibe y **valida** la solicitud con `schemas.ConsultaCreate` (RC-01/RC-02).
- Crea `Subject` + `Consulta` (estado `pending`), **audita** "consulta_creada" y
  **encola** el job en arq (RF-01, RF-03, RF-11).
- Expone estado/resultados, informe y auditoría (RF-09, RF-10, RF-12, RF-13).
- El **pool de arq** se abre en el `lifespan`; si Redis no está, la API sigue viva (RNF-07).

### 4.2 Worker (arq) — `run_consulta`
Es el corazón del "cómo" (RF-03…RF-08):
1. Carga la consulta y el sujeto; marca `running`, `started_at`; audita "consulta_iniciada".
2. Obtiene el scraper con `get_scraper()` (mock o Playwright según config).
3. Abre `results/{slug}.json` y **escribe cada causa a medida que llega** (RF-05, RNF-10).
4. Por cada causa, inserta un `CaseResult` normalizado (RF-06).
5. Al terminar, calcula el score con `risk_engine`, guarda `risk_score/level`,
   marca `done`/`finished_at` y audita "consulta_finalizada" (RF-07).
6. Ante error: rollback, marca `error`, audita "consulta_error" (RNF-07).

### 4.3 Scraper — `services/pjud_scraper.py` (RF-04, RF-14, DD-04)
- **`PjudScraper` (Protocol)**: contrato `scan_persona(...) -> AsyncIterator[CaseRecord]`
  (productor puro; no persiste). El worker consume el generador.
- **`MockPjudScraper`**: datos deterministas por competencia/año, con **homónimos
  demostrativos** (mismo nombre, distinto RUT) para ejercitar RC-04.
- **`PlaywrightPjudScraper`**: skeleton portado de `crawler_nom.py` (helpers
  `_abrir_consulta`, `_wait_tabla`, `_parse_litigantes/relaciones`). Import perezoso de
  Playwright para no cargarlo en el MVP. Competencias **Laboral=4/Penal=5** confirmadas;
  **Civil/Cobranza** marcadas con TODO para verificar en el DOM vivo (RNF-08).
- **`get_scraper()`**: factory según `USE_MOCK_SCRAPER`.

### 4.4 Motor de riesgo — `services/risk_engine.py` (RF-07, RC-03, RC-04)
- `compute_score(cases)` → `{score 0-100, level, factors, homonym_warning, counts, total}`.
- Reglas: peso por competencia (Penal > Cobranza > Laboral ≈ Civil), recencia del año y
  estado (activa/en trámite pesa algo más). Acepta dicts u objetos ORM.
- Los `factors` se redactan como **indicadores a revisar**; **nunca** culpabilidad ni
  recomendación de contratar/no. Si ≥50% son posibles homónimos, activa `homonym_warning`.

### 4.5 Generador de informe — `services/report_generator.py` (RF-08, RC-06)
- `render_report(...)` renderiza `templates/report.html.j2` (Jinja2, autoescape).
- El informe incluye encabezado (sujeto, usuario, motivo, fuente, fecha, parámetros),
  resumen ejecutivo, tabla de hallazgos con **marca de homónimo**, score/nivel/indicadores
  y un **disclaimer** prominente. `save_report(...)` lo guarda en `results/`.

### 4.6 Auditoría — `services/audit_service.py` (RF-11, RC-05, RC-07)
- `log_event(...)` inserta una fila en `audit_logs` (append-only) con usuario, motivo,
  sujeto, fuente, acción y parámetros. Se invoca en creación, inicio, fin, error e informe.

### 4.7 Configuración — `config.py` (RNF-06)
- `Settings` (pydantic-settings) lee `.env`: `DATABASE_URL`, `REDIS_URL`, años por defecto,
  `USE_MOCK_SCRAPER`, `RESULTS_DIR`, `fuente`.
- Mapa `COMPETENCIAS` (nombre → value del `<option>` de la OJV) usado por el scraper real.

## 5. Modelo de datos (RD-01…RD-06)

```
Subject 1───* Consulta 1───* CaseResult
                    │
                    ├──* AuditLog   (append-only; consulta_id nullable)
                    └──* Report
```
- **Consulta.id** es UUID (identificador externo estable). Campos variables
  (`params`, `litigantes`, `relaciones`) se guardan como **JSONB** (RD-06).
- Tablas creadas al arranque con `Base.metadata.create_all` (DD-06); Alembic en fase 2.

## 6. Flujo de una consulta (end-to-end)

```
1. POST /consultas ─▶ valida motivo/años/competencias (422 si falla) ── RC-01/RC-02
2. Crea Subject + Consulta(pending) ─▶ audita "consulta_creada" ─▶ commit
3. Encola run_consulta(id) en Redis (arq)               [respuesta 202 al cliente]
4. Worker toma el job:
   running ─▶ audita "consulta_iniciada"
   por cada causa del scraper:  append a results/{slug}.json  +  insert CaseResult
   compute_score ─▶ guarda score/level ─▶ done ─▶ audita "consulta_finalizada"
5. GET /consultas/{id}         ─▶ estado + causas + conteos + score
6. GET /consultas/{id}/report  ─▶ genera/guarda HTML ─▶ audita "informe_generado"
7. GET /audit                  ─▶ traza completa (usuario/fecha/motivo/sujeto/fuente/params)
```

## 7. Contrato de la API

| Método | Ruta | Requisito |
|--------|------|-----------|
| GET  | `/health` | RF-13 |
| POST | `/consultas` | RF-01, RF-02, RF-03, RC-01/02 |
| GET  | `/consultas` | RF-10 |
| GET  | `/consultas/{id}` | RF-09 |
| GET  | `/consultas/{id}/report` | RF-08 |
| GET  | `/audit` | RF-12 |

## 8. Compliance en el diseño (cómo cumplimos cada RC)

- **RC-01/RC-02** — `motivo` con `min_length` y validación de no-trivial en el schema:
  sin motivo válido, la API responde **422** antes de crear nada.
- **RC-03** — `risk_engine` produce solo indicadores; el informe evita lenguaje de
  culpabilidad/recomendación (verificado por test y por revisión del template).
- **RC-04** — `possible_homonym` en cada causa + aviso en informe/score.
- **RC-05/RC-07** — cada paso escribe en `audit_logs` (append-only) con fuente/fecha/params.
- **RC-06** — disclaimer fijo y prominente en `report.html.j2`.
- **RC-08** — `.env` en `.gitignore`; solo se versiona `.env.sample`.

## 9. Decisiones técnicas y justificación (DD)

| Decisión | Justificación |
|----------|---------------|
| `backend/app/` (DD-01) | Estructura esperada del plan; separa backend del worker/infra. |
| arq sobre Redis (DD-02) | Cola async liviana que encaja con Playwright async; estado de job integrado. |
| LLM/pgvector diferidos (DD-03) | Score/informe rule-based bastan para el MVP; el stack ML es pesado (va en `requirements-ml.txt`). |
| Scraper como productor puro (DD-04) | Desacopla scraping de persistencia; el mock y el real comparten worker. |
| Sin auth (DD-05) | Uso interno; `requested_by` obligatorio. Auth en fase 2. |
| `create_all` al arranque (DD-06) | Simplicidad del MVP; migraciones (Alembic) después. |

## 10. Infraestructura y despliegue (RNF-04)

- **Docker Compose** (raíz): `db` (postgres:16), `redis` (7-alpine), `api` (uvicorn) y
  `worker` (arq), compartiendo imagen `infra/Dockerfile`. `depends_on` con health checks.
- **Volumen** `./results` montado en api y worker (JSON e informes persistentes).
- Arranque: `cp .env.sample .env && docker compose up --build` (CA-06).

## 11. Calidad y pruebas (RNF-09)

- **CI** (GitHub Actions): `ruff check`, import de `app.main` y `pytest`.
- **Tests unitarios** actuales: `risk_engine` (niveles, sin lenguaje prohibido),
  `MockPjudScraper` (emisión + homónimos + determinismo) y validación de `schemas`
  (motivo/años/competencias). Cubren CA-02 y CA-04 parcialmente.
- Pendiente de entorno: prueba end-to-end con Postgres+Redis reales (CA-01/03/05/06).

## 12. Camino a fase 2

1. **Scraper real**: implementar los TODO de `PlaywrightPjudScraper`, verificar los
   `value` de competencia Civil/Cobranza en el DOM vivo y poner `USE_MOCK_SCRAPER=false`.
2. **LLM + semántica**: instalar `requirements-ml.txt`, resumir fallos con llama-cpp y
   habilitar embeddings/pgvector para búsqueda semántica.
3. **Auth + Alembic**: control de acceso corporativo y migraciones versionadas.
4. **Ampliar sujetos**: consulta por RUT y de empresas.

---
_La lista de tareas concreta (desglose ejecutable con estimaciones/prioridades) se
definirá en un paso posterior, tomando este plan y `requirements.md` como base._
