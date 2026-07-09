# Persistencia y backup de Postgres (T-74)

> Política operativa del volumen `dbdata` y de los respaldos de la base. Alineada
> con la retención de datos personales ([`../compliance/data-retention-policy.md`](../compliance/data-retention-policy.md), T-101).
>
> _Fecha: 2026-07-09._

## 1. Persistencia

- La base corre en el servicio `db` (Postgres 16) de `docker-compose.yml` con el
  volumen nombrado **`dbdata`** montado en `/var/lib/postgresql/data`.
- El volumen **persiste** entre `up`/`down`. `docker compose down -v` **borra**
  `dbdata` (destructivo): no usar en producción.
- Con pgvector (`docker-compose.pgvector.yml`) el volumen es el mismo; la extensión
  se crea al inicializar un volumen nuevo o vía `vectorstore.ensure_schema`.

## 2. Backups

### Respaldo lógico (recomendado)

```bash
# Dump comprimido (formato custom) al host
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" \
  > backups/chapi_$(date +%Y%m%d_%H%M%S).dump
```

### Restauración

```bash
docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  --clean --if-exists < backups/chapi_YYYYMMDD_HHMMSS.dump
```

### Respaldo físico (alternativa)

`docker run --rm -v chapi_local_dbdata:/data -v "$PWD/backups:/backup" alpine \
  tar czf /backup/dbdata_$(date +%F).tgz -C /data .` (con la base detenida).

## 3. Frecuencia y retención de backups

⚠️ **DECISIÓN OPERATIVA** (a confirmar): sugerencia por defecto —

| Ítem | Sugerencia |
|------|------------|
| Frecuencia | Diaria (lógico), programado (cron/tarea) |
| Retención de backups | 30 días; 1 mensual por 12 meses |
| Cifrado | Cifrar los dumps en reposo (datos personales) |
| Ubicación | Almacenamiento fuera del host (offsite/objeto) |

Los backups contienen **datos personales**: aplican las mismas obligaciones de
minimización, cifrado y purga que la política de retención (T-101).

## 4. Ciclo del volumen

- **Migraciones de esquema**: en producción, `AUTO_CREATE_TABLES=false` +
  `alembic upgrade head` (T-221) antes de servir tráfico.
- **Recreación**: si se recrea `dbdata`, restaurar desde el último dump y correr
  `alembic upgrade head`.
- **Monitoreo**: vigilar espacio del volumen; alertar al 80% (T-232 expone métricas
  de la app; el disco se vigila a nivel host/infra).

## 5. Checklist de producción

- [ ] Backups automáticos programados y verificados (restore de prueba periódico).
- [ ] Dumps cifrados y offsite.
- [ ] `AUTO_CREATE_TABLES=false` + Alembic.
- [ ] Retención de backups definida y aplicada (§3).
