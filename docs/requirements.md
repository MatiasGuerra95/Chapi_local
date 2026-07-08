# Requisitos — Chapi Local (Due Diligence & Compliance)

> Documento de **requisitos** para uso interno. No incluye la lista de tareas
> (se definirá más adelante). Cada requisito lleva un ID para trazabilidad.

## 1. Contexto y objetivo

Empresa chilena de RRHH, servicios transitorios, outsourcing y reclutamiento
necesita un sistema **interno** de due diligence y compliance que permita:

- Consultar antecedentes públicos de **personas** o **empresas**.
- Guardar la **evidencia** de forma trazable.
- Calcular un **score de riesgo**.
- Generar un **informe** trazable con disclaimer.

El objetivo del MVP es entregar la base funcional (backend + worker + persistencia +
auditoría + informe) con un **scraper mockeado** detrás de una interfaz reemplazable,
dejando preparado el reemplazo por **Playwright real** contra el Poder Judicial.

## 2. Alcance

### 2.1 Dentro del MVP
- Backend en Python con **FastAPI**.
- Persistencia en **PostgreSQL**.
- **Docker Compose** para levantar backend, PostgreSQL y **Redis**.
- **Worker** (cola de trabajos) que ejecuta la búsqueda por nombre en el Poder Judicial.
- Búsqueda que recorre competencias **Civil, Laboral, Penal y Cobranza**.
- Iteración por **años configurables**.
- Guardado de resultados en **tiempo real** en un archivo **JSON por persona**.
- Persistencia de resultados **normalizados** en PostgreSQL.
- **Auditoría**: usuario, fecha, motivo de consulta, sujeto consultado y fuente.
- **Informe HTML** con resumen, hallazgos, score de riesgo y disclaimer.
- **Compliance**: finalidad legítima obligatoria, sin búsquedas sin motivo,
  marca de homónimos, registro de fuente/fecha/parámetros, disclaimer.

### 2.2 Fuera de alcance (fase 2)
- Implementación completa del scraper real con Playwright (ver RNF-08).
- Resúmenes con LLM local (llama-cpp) y búsqueda semántica con embeddings/pgvector.
- Autenticación/autorización de usuarios y migraciones con Alembic.
- Consulta por RUT y de empresas (el MVP se centra en persona por nombre).

## 3. Actores

- **Usuario interno (reclutador / analista de compliance)**: crea consultas con una
  finalidad legítima y revisa los resultados e informes.
- **Persona autorizada / revisor**: valida los hallazgos antes de cualquier decisión.
- **Sistema (worker)**: ejecuta la búsqueda de forma asíncrona.

> Nota: en el MVP no hay sistema de autenticación; el `usuario` se recibe como campo
> obligatorio en la solicitud (`requested_by`). La auth se aborda en fase 2.

## 4. Requisitos funcionales (RF)

| ID | Requisito |
|----|-----------|
| RF-01 | El sistema debe permitir **crear una consulta** de due diligence indicando el sujeto (persona), el usuario solicitante y el motivo (finalidad legítima). |
| RF-02 | El sistema debe permitir configurar los **parámetros de búsqueda**: competencias (Civil/Laboral/Penal/Cobranza) y rango de años (desde/hasta). |
| RF-03 | El sistema debe **encolar** la consulta y procesarla de forma **asíncrona** mediante un worker, sin bloquear la API. |
| RF-04 | El worker debe ejecutar la **búsqueda por nombre** en el Poder Judicial recorriendo las competencias e iterando por cada año del rango. |
| RF-05 | El sistema debe **escribir los resultados en tiempo real** en un archivo **JSON por persona** a medida que se obtienen. |
| RF-06 | El sistema debe **normalizar y persistir** cada causa encontrada en PostgreSQL (competencia, RIT, RUC, tribunal, caratulado, fecha de ingreso, estado, año, litigantes, relaciones). |
| RF-07 | El sistema debe **calcular un score de riesgo** a partir de las causas encontradas y clasificarlo en un nivel (bajo/medio/alto). |
| RF-08 | El sistema debe **generar un informe HTML** con: encabezado (sujeto, usuario, motivo, fuente, fecha, parámetros), resumen ejecutivo, tabla de hallazgos, score/nivel/indicadores y disclaimer. |
| RF-09 | El sistema debe permitir **consultar el estado** de una consulta y sus resultados (causas, conteos, score). |
| RF-10 | El sistema debe permitir **listar** las consultas realizadas. |
| RF-11 | El sistema debe registrar en un **log de auditoría** cada evento relevante (creación, inicio, finalización, error, informe generado). |
| RF-12 | El sistema debe permitir **consultar la auditoría**, con filtro opcional por consulta. |
| RF-13 | El sistema debe exponer un endpoint de **health check**. |
| RF-14 | El scraper debe estar detrás de una **interfaz** que permita reemplazar la implementación **mock** por la **real (Playwright)** sin modificar el worker ni la API. |

## 5. Requisitos de datos

| ID | Requisito |
|----|-----------|
| RD-01 | **Sujeto**: tipo (persona/empresa), nombre, apellidos, RUT (opcional), razón social (opcional). |
| RD-02 | **Consulta**: usuario solicitante, motivo, fuente, parámetros (competencias, años), estado, score/nivel, timestamps (creación/inicio/fin), ruta del JSON de resultados, error (si aplica). |
| RD-03 | **Causa (resultado)**: vínculo a la consulta, competencia, RIT, RUC, tribunal, caratulado, fecha de ingreso, estado, año, litigantes, relaciones, marca de posible homónimo, URL/fuente, fecha de captura. |
| RD-04 | **Auditoría** (append-only): usuario, motivo, sujeto (snapshot), fuente, acción, parámetros, fecha. |
| RD-05 | **Informe**: vínculo a la consulta, ruta del HTML, score, nivel, fecha de generación. |
| RD-06 | Los parámetros y estructuras variables (litigantes, relaciones, parámetros de búsqueda) se almacenan como JSON. |

## 6. Requisitos de compliance y legales (RC)

| ID | Requisito |
|----|-----------|
| RC-01 | Toda consulta debe exigir una **finalidad legítima** (motivo obligatorio y descriptivo). |
| RC-02 | El sistema **no debe permitir búsquedas sin motivo** (rechazo con error de validación). |
| RC-03 | El sistema **no debe afirmar culpabilidad** ni recomendar automáticamente contratar / no contratar; los resultados se presentan como **indicadores a revisar**. |
| RC-04 | El sistema debe **marcar posibles homónimos** (la búsqueda por nombre no confirma identidad; requiere verificación por RUT). |
| RC-05 | El sistema debe **registrar la fuente, la fecha y los parámetros** de cada búsqueda. |
| RC-06 | El informe debe incluir un **disclaimer** indicando que los resultados son preliminares y **deben ser revisados por una persona autorizada**. |
| RC-07 | La auditoría debe ser **trazable** e **inmutable** (append-only). |
| RC-08 | El sistema **no debe exponer ni versionar secretos** (credenciales, tokens, `.env`). |

## 7. Requisitos no funcionales (RNF)

| ID | Requisito |
|----|-----------|
| RNF-01 | **Lenguaje/Framework**: Python 3.12 + FastAPI (API async). |
| RNF-02 | **Persistencia**: PostgreSQL (driver async). ORM con SQLAlchemy 2.0. |
| RNF-03 | **Cola/Worker**: procesamiento asíncrono sobre **Redis** mediante **arq** (compatible con Playwright async). |
| RNF-04 | **Contenedores**: Docker Compose orquesta API, worker, PostgreSQL y Redis; dependencias con health checks. |
| RNF-05 | **Estructura del proyecto**: `backend/app` (main, config, db, models, schemas, routers, services, templates) y `workers/`. |
| RNF-06 | **Configuración por entorno** (variables/`.env`): URLs de DB y Redis, rango de años por defecto, selector de scraper (mock/real), carpeta de resultados. |
| RNF-07 | **Robustez**: si Redis no está disponible, la API sigue operativa (el worker no recibe trabajos); los errores del worker se registran y marcan la consulta como `error`. |
| RNF-08 | **Extensibilidad del scraper**: la implementación real (Playwright) se activa por configuración; los valores de competencia **Laboral=4** y **Penal=5** están confirmados, **Civil y Cobranza** deben verificarse contra el DOM vivo. |
| RNF-09 | **Calidad**: lint (ruff) y pruebas unitarias (pytest) en CI; el pipeline verifica import de la app y ejecuta los tests. |
| RNF-10 | **Trazabilidad de resultados**: JSON por persona en carpeta de resultados + persistencia normalizada; ambos consistentes. |
| RNF-11 | **Internacionalización**: contenido orientado a Chile/español (competencias, informe, disclaimer). |

## 8. Restricciones y decisiones de diseño confirmadas

- **DD-01** — Estructura bajo `backend/app/` (según la estructura esperada del plan).
- **DD-02** — Cola/worker con **arq** sobre Redis (async).
- **DD-03** — LLM (llama-cpp) y **pgvector** **diferidos** a fase 2; el informe y el score
  son **rule-based** en el MVP.
- **DD-04** — El scraper es un **productor puro** (async generator de causas); el worker
  se encarga del JSON en tiempo real y de la persistencia (desacople).
- **DD-05** — Sin autenticación en el MVP; el usuario se recibe como campo obligatorio.
- **DD-06** — Creación de tablas al arranque (MVP); migraciones (Alembic) en fase 2.

## 9. Supuestos

- La OJV del Poder Judicial mantiene la búsqueda por nombre y la estructura de DOM
  usada como referencia (sujeto a verificación al activar el scraper real).
- El uso es **interno** y con finalidad legítima; el control de acceso corporativo
  queda fuera del MVP.
- Los datos consultados son de **fuentes públicas**.

## 10. Criterios de aceptación (alto nivel)

- **CA-01** — Crear una consulta con motivo válido devuelve estado inicial; el worker
  la procesa y queda `done` con causas y score.
- **CA-02** — Crear una consulta **sin motivo** (o trivial) es **rechazada** por validación.
- **CA-03** — Existe un **JSON por persona** escrito incrementalmente durante el procesamiento.
- **CA-04** — El **informe HTML** contiene resumen, tabla de hallazgos, score, marca de
  homónimos y disclaimer; no contiene afirmaciones de culpabilidad ni recomendaciones.
- **CA-05** — La **auditoría** refleja los eventos (creación, inicio, fin, informe) con
  usuario, fecha, motivo, sujeto, fuente y parámetros.
- **CA-06** — El stack completo levanta con `docker compose up` (API, worker, DB, Redis).

## 11. Referencias

- Plan inicial y decisiones: `.claude/plans/necesito-construir-una-aplicaci-n-breezy-graham.md`.
- Scraper de referencia (a portar en fase 2): `crawler_nom.py`, `detalle.py`, `extractor.py`.
- Documentación de uso y arquitectura: `README.md`.
