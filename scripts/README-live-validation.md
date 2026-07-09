# Validación en vivo del scraper real (T-200 / T-205)

Guía para validar `PlaywrightPjudScraper` contra la OJV del Poder Judicial en un
entorno controlado. **Prerequisito de compliance:** gate legal levantado (T-100) y
politeness configurada (T-104). El modo por defecto sigue siendo **mock**; nada de
esto altera `docker compose up` normal.

## 0. Preparar `.env`

```bash
cp .env.sample .env    # si aún no existe
```

Deja `USE_MOCK_SCRAPER=true` (el overlay lo desactiva sólo para el worker). Ajusta
la politeness si la fuente lo exige:

```env
SCRAPER_MIN_DELAY_SECONDS=1.5
SCRAPER_JITTER_SECONDS=0.7
```

## 1. Levantar el stack en modo vivo (worker con Chromium)

```bash
docker compose -f docker-compose.yml -f docker-compose.live.yml up --build
```

Esto construye el **worker** con Chromium (`INSTALL_BROWSERS=true`, descarga
pesada la primera vez) y fija `USE_MOCK_SCRAPER=false` sólo en el worker. La API se
mantiene liviana (sin navegador).

## 2. Confirmar valores de competencia (T-200)

Antes de confiar en Civil/Cobranza, vuelca los `value` reales de `#nomCompetencia`:

```bash
docker compose -f docker-compose.yml -f docker-compose.live.yml \
    exec worker python /app/scripts/inspect_ojv.py
# Listar además los tribunales de una competencia (por su value):
docker compose -f docker-compose.yml -f docker-compose.live.yml \
    exec worker python /app/scripts/inspect_ojv.py --tribunales 3
```

Si Civil/Cobranza difieren de los placeholders (`Civil="3"`, `Cobranza="7"`) o los
sufijos del modal (`Civ`/`Cob`) no coinciden, ajusta `COMPETENCIAS` y
`COMPETENCIA_SUFIJO` en `backend/app/config.py` y marca T-200 como cerrado.

## 3. Ejecutar una consulta acotada y validar (T-205)

Desde el **host** (sólo usa la API por HTTP, no necesita navegador):

```bash
python scripts/validate_live.py \
    --nombre "SERGIO ANDRES" --ape-paterno COVARRUBIAS --ape-materno VALENZUELA \
    --competencia Penal --year 2011
```

El script hace readiness, crea la consulta (1 competencia / 1 año para no golpear la
fuente), hace polling y reporta causas, score, homónimos y conteos, además de dónde
quedaron el JSON (`./results/`) y el informe (`/consultas/{id}/report`).

Si `API_KEY` está configurada, pásala con `--api-key` o `export API_KEY=...`.

## 4. Revisar evidencia

- **JSON por persona**: `./results/{slug}.json` (montado como volumen).
- **Informe**: `http://localhost:8000/consultas/{id}/report`.
- **Auditoría**: `http://localhost:8000/audit?consulta_id={id}`.
- **Logs con correlación** (job-id): `docker compose ... logs -f worker`.

## Notas

- El scraper es lento (muchos tribunales × años). El `job_timeout` de arq está
  subido a 1800 s (`ARQ_JOB_TIMEOUT_SECONDS`); acota siempre la consulta.
- `--no-sandbox`/`--disable-dev-shm-usage` ya están fijados para Chromium en
  contenedor.
- Cierra el gate técnico actualizando `docs/tasks.md` (T-200/T-203/T-205) y
  `docs/STATUS.md` cuando la validación pase.
