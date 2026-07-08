# Chapi Local — Due Diligence & Compliance (MVP)

Sistema **interno** para una empresa de RRHH / servicios transitorios / outsourcing.
Permite consultar antecedentes públicos (Poder Judicial), guardar evidencia trazable,
calcular un **score de riesgo** rule-based y generar un **informe HTML** con disclaimer.

> ⚠️ Uso responsable: toda consulta exige una **finalidad legítima** (motivo). Los
> resultados son **preliminares**, no afirman culpabilidad ni recomiendan contratar/no
> contratar, y **deben ser revisados por una persona autorizada**. La búsqueda por nombre
> puede arrojar **homónimos** (verificar por RUT).

## Arquitectura

- **API FastAPI** (`backend/app`) — crea consultas, expone estado, informe y auditoría.
- **Worker arq** (`workers/judicial_worker.py`) — procesa la consulta en segundo plano:
  ejecuta el scraper, escribe **JSON en tiempo real** por persona en `results/`,
  persiste causas normalizadas en Postgres, calcula el score y audita cada paso.
- **PostgreSQL** — persistencia (`subjects`, `consultas`, `case_results`, `audit_logs`, `reports`).
- **Redis** — cola de trabajos (arq).
- **Scraper** (`backend/app/services/pjud_scraper.py`) — interfaz `PjudScraper` con
  `MockPjudScraper` (por defecto) y `PlaywrightPjudScraper` (skeleton, fase 2).

```
backend/app/{main,config,db,models,schemas}.py
backend/app/routers/{health,consultas,audit}.py
backend/app/services/{pjud_scraper,risk_engine,report_generator,audit_service}.py
backend/app/templates/report.html.j2
workers/judicial_worker.py
infra/Dockerfile · docker-compose.yml
```

## Puesta en marcha (Docker)

```bash
cp .env.sample .env
docker compose up --build
```

Levanta `db`, `redis`, `api` (http://localhost:8000) y `worker`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET  | `/health` | Estado del servicio |
| POST | `/consultas` | Crea consulta (requiere `motivo`), audita y encola |
| GET  | `/consultas` | Lista consultas |
| GET  | `/consultas/{id}` | Estado + causas + conteos |
| GET  | `/consultas/{id}/report` | Informe HTML (con disclaimer) |
| GET  | `/audit` | Trazabilidad (filtro opcional `?consulta_id=`) |

### Ejemplo

```bash
curl -X POST http://localhost:8000/consultas -H 'Content-Type: application/json' -d '{
  "subject": {"nombre": "Sergio Andrés", "ape_paterno": "Covarrubias", "ape_materno": "Valenzuela"},
  "requested_by": "reclutador@empresa.cl",
  "motivo": "Debida diligencia previa a contratación",
  "competencias": ["Civil", "Laboral", "Penal", "Cobranza"],
  "year_from": 2018,
  "year_to": 2024
}'
# -> 202 { "id": "<uuid>", "status": "pending", ... }

curl http://localhost:8000/consultas/<uuid>          # estado + causas + score
curl http://localhost:8000/consultas/<uuid>/report   # informe HTML
curl http://localhost:8000/audit                     # trazabilidad
```

## Desarrollo local (sin Docker)

Requiere Postgres y Redis locales (ajusta `DATABASE_URL`/`REDIS_URL` en `.env`).

```bash
pip install -r requirements.txt
export PYTHONPATH=backend
uvicorn app.main:app --reload --app-dir backend      # API
arq workers.judicial_worker.WorkerSettings           # worker
pytest -q                                            # tests
```

## Compliance

- **Finalidad legítima obligatoria**: `motivo` (≥10 caracteres) o la consulta es rechazada (422).
- **Auditoría append-only**: usuario, fecha, motivo, sujeto, fuente y parámetros en cada paso.
- **Homónimos**: la búsqueda por nombre marca `possible_homonym`; el informe lo advierte.
- **Sin juicios**: el score entrega *indicadores a revisar*, nunca culpabilidad ni recomendación.
- **Disclaimer** obligatorio en el informe.

## Fase 2 (fuera del MVP)

- Playwright real completo (verificar `value` de **Civil/Cobranza** en `#nomCompetencia` del
  DOM vivo; Laboral=`4` y Penal=`5` ya confirmados). Cambiar `USE_MOCK_SCRAPER=false`.
- LLM local (`llama-cpp`) para resumen de fallos + embeddings/pgvector (ver `requirements-ml.txt`).
- Autenticación de usuarios y migraciones Alembic.
- Consulta por RUT y de empresas.
