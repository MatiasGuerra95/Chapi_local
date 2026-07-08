"""Motor de riesgo rule-based.

Produce indicadores para revisión humana. NO afirma culpabilidad ni recomienda
contratar/no contratar. La búsqueda por nombre implica posibles homónimos.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Iterable

# Peso base por competencia (indicador, no juicio de culpabilidad).
COMPETENCIA_WEIGHTS: dict[str, float] = {
    "Penal": 30.0,
    "Cobranza": 20.0,
    "Laboral": 12.0,
    "Civil": 10.0,
}
_DEFAULT_WEIGHT = 8.0
_ACTIVA_HINTS = ("trami", "activ", "vigente", "en curso")


def _field(case: Any, name: str) -> Any:
    if isinstance(case, dict):
        return case.get(name)
    return getattr(case, name, None)


def compute_score(cases: Iterable[Any], current_year: int | None = None) -> dict:
    """Calcula score 0-100, nivel y factores. Acepta dicts u objetos ORM."""
    cases = list(cases)
    current_year = current_year or date.today().year

    if not cases:
        return {
            "score": 0.0,
            "level": "bajo",
            "factors": ["Sin causas encontradas para los parámetros indicados."],
            "homonym_warning": False,
            "counts": {},
            "total": 0,
        }

    score = 0.0
    counts: dict[str, int] = {}
    homonimos = 0

    for c in cases:
        comp = _field(c, "competencia") or "Otro"
        counts[comp] = counts.get(comp, 0) + 1
        weight = COMPETENCIA_WEIGHTS.get(comp, _DEFAULT_WEIGHT)

        year = _field(c, "year") or current_year
        try:
            antiguedad = current_year - int(year)
        except (TypeError, ValueError):
            antiguedad = 0
        recencia = 1.0 if antiguedad <= 3 else 0.6

        estado = (_field(c, "estado") or "").lower()
        actividad = 1.15 if any(h in estado for h in _ACTIVA_HINTS) else 1.0

        score += weight * recencia * actividad
        if _field(c, "possible_homonym"):
            homonimos += 1

    score = min(100.0, round(score, 1))
    level = "bajo" if score < 25 else "medio" if score < 60 else "alto"

    factors: list[str] = []
    for comp, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        factors.append(f"{n} causa(s) en competencia {comp} (indicador a revisar).")

    homonym_warning = homonimos > 0 and homonimos >= len(cases) * 0.5
    if homonym_warning:
        factors.append(
            "Posibles homónimos: la búsqueda fue por nombre. "
            "Verifique la identidad por RUT antes de concluir."
        )

    return {
        "score": score,
        "level": level,
        "factors": factors,
        "homonym_warning": homonym_warning,
        "counts": counts,
        "total": len(cases),
    }
