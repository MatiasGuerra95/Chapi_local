"""Utilidades de RUT chileno y desambiguación de homónimos (T-222, RC-04).

La búsqueda por nombre no confirma identidad (posible homónimo). Cuando el sujeto
consultado tiene RUT y una causa lo lista entre sus litigantes, esa causa **sí**
corresponde al sujeto: se puede desmarcar el homónimo.
"""
from __future__ import annotations

import re
from typing import Any

_CLEAN = re.compile(r"[.\s-]")


def normalize(rut: Any) -> str:
    """Normaliza un RUT a la forma canónica ``CUERPO-DV`` (sin puntos, DV en mayúscula).

    Devuelve "" si no hay RUT utilizable. Ignora ceros a la izquierda del cuerpo
    para tolerar formatos distintos entre fuentes.
    """
    if not rut:
        return ""
    s = _CLEAN.sub("", str(rut)).upper()
    if len(s) < 2 or not s[:-1].isdigit():
        return ""
    body, dv = s[:-1].lstrip("0"), s[-1]
    return f"{body}-{dv}" if body else ""


def confirms_identity(litigantes: Any, subject_rut: Any) -> bool:
    """True si algún litigante tiene el mismo RUT (normalizado) que el sujeto."""
    target = normalize(subject_rut)
    if not target:
        return False
    for lit in litigantes or []:
        rut = lit.get("rut") if isinstance(lit, dict) else None
        if normalize(rut) == target:
            return True
    return False
