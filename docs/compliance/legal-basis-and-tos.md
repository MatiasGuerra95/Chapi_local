# Base de licitud y Términos de Uso (OJV/PJUD) — Chapi Local

> **Estado: CERRADO — decisiones adoptadas por el responsable (product owner) el 2026-07-09.**
> Este documento estructuró la revisión y **registra** las decisiones tomadas.
> **No constituye asesoría legal**; las decisiones fueron provistas por el
> responsable del producto y deben mantenerse alineadas con el área legal.
>
> _Fecha: 2026-07-09 · Marco: Ley 19.628 y Ley 21.719 (Chile)._

## 0. Decisiones adoptadas (2026-07-09)

| # | Punto | Decisión |
|---|-------|----------|
| §3 | Base de licitud | **Ambas**: consentimiento del candidato como base principal, **reforzada** con interés legítimo del empleador (con test de ponderación documentado). |
| §5 | ToS de la OJV | **Revisados: permiten** la consulta automatizada → se **habilita** el desarrollo/activación del scraper real. Confirmación asumida por el responsable. |
| §4 | Causas penales | **Incluir con revisión humana** caso a caso y verificación de identidad (RC-03/RC-04/RC-06); no descartar automáticamente. |

> Retención de datos: ver decisiones en [`data-retention-policy.md`](./data-retention-policy.md) §0.
> Estas decisiones **levantan el gate** de T-100 sobre Fase 2 (scraper real). Se
> mantienen las salvaguardas de compliance (homónimos, sin culpabilidad, revisión
> humana, auditoría, politeness/T-104).

## 1. Objeto

Determinar (a) la **base de licitud** del tratamiento de datos personales que
realiza Chapi Local y (b) si los **Términos de Uso** de la Oficina Judicial Virtual
(OJV) del Poder Judicial permiten la **consulta automatizada** (scraping) por
nombre. Ambas condiciones son **prerequisito** para habilitar el scraper real.

## 2. Naturaleza de los datos

- La OJV expone información de **causas judiciales** de acceso público.
- Que la fuente sea pública **no elimina** las obligaciones de la normativa de
  datos personales al **recolectar, tratar y perfilar** esa información con una
  finalidad propia (evaluación de candidatos).
- Las causas **penales** pueden constituir **datos sensibles / relativos a
  infracciones**; su uso en decisiones laborales es especialmente delicado
  (presunción de inocencia, no discriminación).

## 3. Base de licitud (a confirmar)

Opciones bajo Ley 19.628 / 21.719, a evaluar por legal:

| Base | Aplicabilidad | Observaciones |
|------|---------------|---------------|
| **Interés legítimo** del empleador | Candidata principal | Requiere test de ponderación frente a los derechos del titular y minimización |
| **Consentimiento** del titular (candidato) | Posible/complementaria | Debe ser libre e informado; el desbalance empleador-candidato lo debilita |
| Datos de **fuente de acceso público** | Habilita el acceso, no exime el tratamiento | Persisten deberes de finalidad, proporcionalidad y derechos |

✅ **RESUELTO (§0)**: base **ambas** (consentimiento + interés legítimo). Pendiente
operativo: documentar el **test de ponderación** y el flujo de consentimiento.

## 4. Finalidad y proporcionalidad

- Finalidad declarada: **due diligence de contratación** con motivo registrado
  (RC-01, ya exigido y reforzado — ver T-105).
- Proporcionalidad: limitar competencias/años a lo necesario; evitar el tratamiento
  masivo o especulativo. ✅ **RESUELTO (§0)**: las causas **penales** se **incluyen
  con revisión humana** caso a caso (no descarte automático).

## 5. Términos de Uso y aspectos técnico-legales de la OJV

✅ **RESUELTO (§0)**: revisados y **permiten** la consulta automatizada. Se mantiene
la política de *politeness* (T-104) acorde a los límites de la fuente. Elementos a
seguir vigilando de forma operativa:

- [x] **Términos y Condiciones de Uso** de la OJV/PJUD: revisados, permiten el uso.
- [x] **`robots.txt`** y avisos del sitio (`oficinajudicialvirtual.pjud.cl`).
- [ ] **CAPTCHA / sesión / JWT** para el detalle (cf. `detalle.py`) — manejo técnico
      en T-203.
- [x] **Límites de uso**: cubiertos por los parámetros de politeness (T-104).
- [ ] Vía **oficial/API** alternativa a la extracción por DOM, si apareciera.

## 6. Riesgos identificados

- **Legal/contractual**: incumplir los ToS de la OJV; tratamiento sin base de
  licitud sólida.
- **Discriminación**: uso de causas (esp. penales) para descartar candidatos sin
  ponderación caso a caso ni verificación de identidad.
- **Homónimos**: la búsqueda por nombre **no confirma identidad** (ya se marca
  `possible_homonym`, RC-04); decidir con datos de un homónimo sería lesivo.
- **Operacional**: bloqueo/limitación por parte de la fuente ante scraping agresivo
  (mitigado parcialmente por T-104).

## 7. Condiciones para habilitar el scraper real (gate)

Antes de `USE_MOCK_SCRAPER=false` (T-205), se recomienda tener **cerrados**:

1. ✅ Base de licitud definida (§0/§3): consentimiento + interés legítimo.
2. ✅ Revisión de ToS/robots.txt de la OJV con conclusión explícita (§0/§5): permitido.
3. ✅ Política de retención aprobada ([`data-retention-policy.md`](./data-retention-policy.md), T-101).
4. ✅ Parámetros de politeness acordes a los límites de la fuente (T-104).
5. ✅ Control de acceso y minimización operativos (T-102).
6. ⏳ Procedimiento de revisión humana y manejo de homónimos (RC-03, RC-04, RC-06) —
   soportado por el producto; formalizar el flujo operativo con RRHH.

**Gate levantado**: se habilita el desarrollo de Fase 2 y la activación del scraper
real tras la validación técnica en entorno controlado (T-200/T-205).

## 8. Preguntas abiertas para legal

- ¿Base de licitud primaria y su documentación?
- ¿Los ToS de la OJV permiten la consulta automatizada? Si no, ¿vía oficial?
- ¿Tratamiento admisible de causas penales en selección de personal?
- ¿Plazos de retención y postura sobre supresión vs. auditoría (T-101 §5)?

## 9. Referencias

- Ley 19.628 sobre protección de la vida privada (Chile).
- Ley 21.719 sobre protección de datos personales (Chile).
- OJV — Oficina Judicial Virtual del Poder Judicial: `https://oficinajudicialvirtual.pjud.cl`.
- Requisitos internos: `docs/requirements.md` (RC-01…RC-08), `docs/tasks.md` (T-100, T-200+).

---
_Relacionado: [`data-retention-policy.md`](./data-retention-policy.md) (T-101)._
