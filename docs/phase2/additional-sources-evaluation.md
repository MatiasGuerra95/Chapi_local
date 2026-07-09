# Evaluación de fuentes adicionales (T-233)

> Análisis para due diligence más allá del Poder Judicial (OJV). **No** implementa
> las fuentes: evalúa candidatas, su acceso/legalidad y cómo encajan en la
> arquitectura actual. Cada fuente nueva requiere su propia base de licitud y
> revisión de ToS (ver [`../compliance/legal-basis-and-tos.md`](../compliance/legal-basis-and-tos.md), T-100).
>
> _Fecha: 2026-07-09._

## 1. Criterios de evaluación

Valor para due diligence · método de acceso (API oficial > scraping) · legalidad/ToS ·
calidad y frescura del dato · esfuerzo de integración · riesgo de homónimos.

## 2. Fuentes candidatas

| Fuente | Qué aporta | Acceso | Legalidad | Valor | Esfuerzo |
|--------|------------|--------|-----------|-------|----------|
| **Boletín Comercial** (Cámara de Comercio / DICOM-Equifax) | Protestos y morosidades comerciales | Comercial (pago), API/consulta | Requiere contrato y base de licitud clara | Alto (solvencia) | Medio |
| **Inhabilidades para contratar con el Estado** (ChileCompra / Registro de sanciones) | Sanciones e inhabilidades de proveedores | Portal público / posible API | Datos públicos; verificar ToS | Alto (empresas/proveedores) | Medio |
| **Diario Oficial** | Publicaciones legales, constitución/quiebra de sociedades | Web pública, buscador | Público | Medio | Medio-alto (parseo) |
| **Registro Civil — defunciones** | Descartar/validar identidad (fallecidos) | Restringido | Sensible; base de licitud estricta | Bajo-medio | Alto |
| **TGR / deudas fiscales** | Deuda tributaria | Restringido | Sensible | Medio | Alto |
| **Superintendencias (SMV/CMF, sanciones)** | Sanciones sectoriales | Web pública | Público | Medio (según cargo) | Medio |

## 3. Encaje arquitectónico

La arquitectura actual ya está preparada para multi-fuente: el scraper es un
**productor puro** detrás de un `Protocol` (`PjudScraper.scan_persona` → async
generator de `CaseRecord`). Generalización propuesta:

- Definir un `Protocol` genérico `EvidenceSource` con `scan(subject, params) ->
  AsyncIterator[EvidenceRecord]`, del que `PjudScraper` es un caso.
- El worker consumiría **varias** fuentes por consulta (una carpeta/JSON por fuente
  o un JSON unificado con campo `source`), persistiendo evidencia normalizada.
- `CaseResult`/evidencia lleva ya `source_url`; añadir un campo `source` (p.ej.
  `pjud` | `boletin_comercial` | `chilecompra`) para trazar el origen.
- `risk_engine` pondera por tipo de indicador y **por fuente** (hoy pondera por
  competencia); extender `COMPETENCIA_WEIGHTS` a un esquema por fuente+categoría.
- Reutilizar `throttle.py` (politeness/backoff) y el patrón mock/real por fuente.

Cambios menores, sin reescritura: el desacople productor/worker (DD-04) permite
sumar fuentes sin tocar la API.

## 4. Riesgos transversales

- **Legalidad por fuente**: cada una necesita base de licitud y ToS propios (T-100).
  Las fuentes comerciales (Boletín/DICOM) requieren contrato.
- **Homónimos**: agravado al cruzar fuentes; la desambiguación por RUT (T-222) es
  clave y debe aplicarse consistentemente.
- **Datos sensibles**: TGR/Registro Civil elevan el nivel de sensibilidad y de
  minimización.

## 5. Recomendación (priorización)

1. **Inhabilidades ChileCompra** e **Boletín Comercial** — mayor valor para
   contratación/proveedores; empezar por la que tenga acceso oficial/contrato.
2. **Diario Oficial** — complementa el panorama societario de empresas (T-223).
3. Diferir fuentes restringidas (Registro Civil, TGR) hasta tener base de licitud
   sólida y necesidad concreta por cargo.

Antes de implementar cualquiera: (a) cerrar su revisión legal/ToS, (b) generalizar
el `Protocol` a `EvidenceSource`, (c) añadir el campo `source` y la ponderación por
fuente en `risk_engine`.
