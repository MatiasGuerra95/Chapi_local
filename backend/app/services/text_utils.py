"""Normalización de texto de entrada para el scraper real (T-33, RNF-08).

La OJV suele mostrar nombres en mayúsculas; normalizamos la entrada (espacios,
mayúsculas) preservando los caracteres del español (ñ, tildes) para no perder
coincidencias. Se aplica sólo al alimentar los campos del scraper real.
"""
from __future__ import annotations


def normalize_name(value: str | None) -> str:
    """Recorta, colapsa espacios y pasa a mayúsculas. Conserva ñ/tildes."""
    if not value:
        return ""
    return " ".join(str(value).split()).upper()
