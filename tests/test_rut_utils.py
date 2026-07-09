"""T-222/RC-04: normalización de RUT y desambiguación de homónimos."""
import pytest

from app.services.rut_utils import confirms_identity, normalize


@pytest.mark.parametrize(
    "raw,esperado",
    [
        ("12.345.678-9", "12345678-9"),
        ("123456789", "12345678-9"),
        ("12345678-9", "12345678-9"),
        ("0.987.654-K", "987654-K"),
        ("  9.876.543-2 ", "9876543-2"),
        ("", ""),
        (None, ""),
        ("abc", ""),
        ("1", ""),
    ],
)
def test_normalize(raw, esperado):
    assert normalize(raw) == esperado


def test_confirms_identity_match():
    litigantes = [{"tipo": "Demandado", "nombre": "X", "rut": "12.345.678-9"}]
    assert confirms_identity(litigantes, "12345678-9") is True


def test_confirms_identity_sin_match():
    litigantes = [{"rut": "9.876.543-2"}]
    assert confirms_identity(litigantes, "12345678-9") is False


def test_confirms_identity_sin_rut_del_sujeto():
    assert confirms_identity([{"rut": "12.345.678-9"}], None) is False


def test_confirms_identity_litigantes_vacios():
    assert confirms_identity([], "12345678-9") is False
    assert confirms_identity(None, "12345678-9") is False


def test_desambiguacion_desmarca_homonimo():
    # Reproduce la decisión del worker sobre un registro de causa.
    rec = {"possible_homonym": True, "litigantes": [{"rut": "12.345.678-9"}]}
    if confirms_identity(rec["litigantes"], "12.345.678-9"):
        rec["possible_homonym"] = False
    assert rec["possible_homonym"] is False


def test_desambiguacion_mantiene_homonimo_si_no_hay_match():
    rec = {"possible_homonym": True, "litigantes": [{"rut": "9.876.543-2"}]}
    if confirms_identity(rec["litigantes"], "12.345.678-9"):
        rec["possible_homonym"] = False
    assert rec["possible_homonym"] is True
