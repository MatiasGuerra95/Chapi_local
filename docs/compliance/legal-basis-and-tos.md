# Base de licitud y Términos de Uso (OJV/PJUD) — Chapi Local

> **Estado: BORRADOR — requiere validación legal (T-100).**
> Documento de trabajo para estructurar la revisión legal. **No constituye
> asesoría legal.** Los puntos `⚠️ DECISIÓN REQUERIDA` deben resolverse con el
> área legal **antes de activar el scraper real** (bloquea T-200+).
>
> _Fecha: 2026-07-09 · Marco: Ley 19.628 y Ley 21.719 (Chile)._

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

⚠️ **DECISIÓN REQUERIDA**: definir la base de licitud primaria y documentar el
**test de ponderación** (interés legítimo) o el mecanismo de consentimiento.

## 4. Finalidad y proporcionalidad

- Finalidad declarada: **due diligence de contratación** con motivo registrado
  (RC-01, ya exigido y reforzado — ver T-105).
- Proporcionalidad: limitar competencias/años a lo necesario; evitar el tratamiento
  masivo o especulativo. ⚠️ **DECISIÓN REQUERIDA**: ¿se restringen las causas
  **penales** o se excluyen salvo justificación específica del cargo?

## 5. Términos de Uso y aspectos técnico-legales de la OJV

⚠️ **DECISIÓN/REVISIÓN REQUERIDA** — verificar contra las fuentes vigentes:

- [ ] **Términos y Condiciones de Uso** publicados de la OJV/PJUD: ¿prohíben el
      acceso automatizado, la extracción sistemática o la reutilización?
- [ ] **`robots.txt`** y avisos del sitio (`oficinajudicialvirtual.pjud.cl`).
- [ ] Existencia de **CAPTCHA / sesión / JWT** cuya elusión pudiera infringir los
      términos (cf. `detalle.py` de referencia).
- [ ] **Límites de uso** o de tasa esperados por la fuente (define los parámetros de
      politeness — ver T-104).
- [ ] Vía **oficial/API** alternativa a la extracción por DOM, si existiera.

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

1. Base de licitud definida y documentada (§3).
2. Revisión de ToS/robots.txt de la OJV con conclusión explícita (§5).
3. Política de retención aprobada ([`data-retention-policy.md`](./data-retention-policy.md), T-101).
4. Parámetros de politeness acordes a los límites de la fuente (T-104).
5. Control de acceso y minimización operativos (T-102) — **hecho**.
6. Procedimiento de revisión humana y manejo de homónimos (RC-03, RC-04, RC-06).

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
