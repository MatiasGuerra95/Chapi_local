# Política de retención y eliminación de datos personales — Chapi Local

> **Estado: APROBADO — decisiones adoptadas por el responsable (product owner) el 2026-07-09.**
> Registra la política aprobada. **No constituye asesoría legal**; debe mantenerse
> alineada con el área legal y revisarse al entrar en vigor la Ley 21.719.
>
> _Fecha: 2026-07-09 · Marco: Ley 19.628 (protección de la vida privada) y_
> _Ley 21.719 (protección de datos personales, Chile)._

## 0. Decisiones adoptadas (2026-07-09)

| # | Punto | Decisión |
|---|-------|----------|
| §4 | Plazos de retención | **Se adoptan los plazos propuestos**: 6 meses para no contratados; contratados = duración de la relación + plazo legal laboral aplicable; derivados (JSON/informes) siguen a su consulta. |
| §5 | Auditoría vs. supresión | **Se adopta**: no se borran filas de auditoría; al vencer la retención se **eliminan/seudonimizan** los datos personales sustantivos y se conserva la evidencia mínima del tratamiento. |

> Pendiente de implementación técnica (no bloqueante): `RETENTION_DAYS` + tarea de
> purga que respete §5/§6. Ver [`legal-basis-and-tos.md`](./legal-basis-and-tos.md) §0.

## 1. Objeto y alcance

Definir **cuánto tiempo** se conservan los datos personales tratados por Chapi
Local y **cómo se eliminan** al vencer ese plazo o cuando desaparece la finalidad
legítima que justificó su tratamiento. Aplica a todos los datos generados por una
consulta de due diligence: sujeto consultado, motivo, causas obtenidas, archivos
de resultados, informes y auditoría.

## 2. Principios rectores

- **Finalidad y proporcionalidad**: los datos sólo se tratan para la due diligence
  con finalidad legítima registrada (motivo). No se reutilizan para otros fines.
- **Limitación de la conservación**: no se conservan más allá de lo necesario para
  la finalidad; vencido el plazo, se eliminan o anonimizan.
- **Minimización**: se almacena lo mínimo necesario (ver inventario).
- **Trazabilidad e integridad de la auditoría**: la auditoría es *append-only*
  (RC-07); su tratamiento en la eliminación se aborda en §5.

## 3. Inventario de datos personales tratados

| Dato | Modelo/artefacto | Contiene datos personales | Notas |
|------|------------------|---------------------------|-------|
| Sujeto consultado | `subjects` | Sí (nombre, apellidos, RUT) | Identifica al titular |
| Motivo / finalidad | `consultas.motivo` | Indirecto (contexto laboral) | Evidencia de licitud (RC-01) |
| Causas judiciales | `case_results` | Sí (incl. **causas penales** = datos sensibles) | Litigantes/relaciones en JSONB |
| JSON por persona | `results/{slug}.json` | Sí | Copia en disco de las causas |
| Informe HTML | `reports` + archivo | Sí | Resultado presentado al revisor |
| Auditoría | `audit_logs` | Sí (usuario, motivo, snapshot del sujeto) | *Append-only*, inmutable |

> **Nota de sensibilidad**: las causas de competencia **Penal** pueden constituir
> datos sensibles / relativos a infracciones. Su conservación exige especial
> cautela (ver también el análisis de licitud, T-100).

## 4. Plazos de retención propuestos

✅ **ADOPTADO (§0)** — los plazos siguientes fueron **aprobados** por el responsable.

| Categoría | Plazo propuesto (por defecto) | Fundamento |
|-----------|-------------------------------|------------|
| Datos del proceso de selección **no contratado** | **6 meses** desde la decisión | Plazo razonable para eventuales reclamos del postulante |
| Datos asociados a persona **contratada** | Mientras dure la relación + plazo legal laboral aplicable | Vinculación al expediente laboral |
| JSON de resultados / informes | Igual que la categoría de la consulta | Son derivados de las causas |
| Registros de auditoría | **≥ el plazo de la consulta**; ver §5 | Deber de trazabilidad vs. supresión |

Parámetro técnico previsto: `RETENTION_DAYS` (config) para el barrido automático de
las categorías con plazo fijo. **Pendiente de implementación** hasta confirmar §4/§5.

## 5. Auditoría vs. derecho de supresión (tensión a resolver)

La auditoría es *append-only* e inmutable (RC-07) para garantizar trazabilidad de
quién consultó qué y con qué finalidad. Esto **coexiste en tensión** con el derecho
de supresión del titular. Propuesta a validar:

- **No** borrar filas de auditoría (preserva la integridad del registro).
- Al vencer la retención, **eliminar/anonimizar los datos personales sustantivos**
  (sujeto, causas, JSON, informe) y **conservar** en auditoría sólo la evidencia
  mínima del tratamiento (fecha, acción, usuario, finalidad), **seudonimizando** el
  snapshot del sujeto si legal lo exige.
- ✅ **ADOPTADO (§0)**: al vencer la retención, la auditoría **seudonimiza** el
  snapshot del sujeto y conserva la evidencia mínima del tratamiento (no se borran
  filas). Revisable si un deber probatorio específico exigiera lo contrario.

## 6. Procedimiento de eliminación

1. **Identificación**: seleccionar consultas cuya fecha supere el plazo de su
   categoría (§4).
2. **Eliminación de datos sustantivos**: `case_results`, `reports` y el sujeto (si
   no tiene otras consultas vigentes); borrar los archivos `results/*.json` e
   informes HTML asociados.
3. **Auditoría**: registrar un evento `datos_eliminados` (no se borran filas
   previas) y aplicar la seudonimización acordada en §5.
4. **Periodicidad**: barrido programado (p. ej. diario/semanal) — **pendiente**.
5. **Registro de la eliminación**: dejar constancia auditable de qué se eliminó y
   cuándo.

## 7. Derechos del titular (ARCOP)

Definir el canal y el plazo de respuesta para el ejercicio de derechos de acceso,
rectificación, cancelación/supresión, oposición y portabilidad. ⚠️ **DECISIÓN
REQUERIDA**: responsable interno y SLA de respuesta.

## 8. Enforcement técnico (estado)

- **Hoy**: la eliminación no está automatizada; el modelo de datos ya soporta el
  borrado en cascada de causas/informes por consulta (`cascade="all, delete-orphan"`).
- **Pendiente** (tras confirmar §4/§5): añadir `RETENTION_DAYS`, un script/tarea de
  purga que respete la política de auditoría (§5) y su registro (§6.3).

## 9. Revisión

Revisar esta política al entrar en vigor la Ley 21.719 y ante cambios en la
finalidad del tratamiento o en la fuente (OJV/PJUD).

---
_Relacionado: [`legal-basis-and-tos.md`](./legal-basis-and-tos.md) (T-100),_
_`docs/requirements.md` (RC-01, RC-05, RC-07), `docs/tasks.md` (T-101, T-102, T-105)._
