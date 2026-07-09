"""T-33: normalización de nombre/apellidos para el scraper real."""
import pytest

from app.services.text_utils import normalize_name


@pytest.mark.parametrize(
    "raw,esperado",
    [
        ("  juan  carlos ", "JUAN CARLOS"),
        ("peña", "PEÑA"),
        ("José  Ramón", "JOSÉ RAMÓN"),
        ("", ""),
        (None, ""),
        ("Ya MAYUS", "YA MAYUS"),
    ],
)
def test_normalize_name(raw, esperado):
    assert normalize_name(raw) == esperado
