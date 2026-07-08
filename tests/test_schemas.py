import pytest
from pydantic import ValidationError

from app import schemas


def test_motivo_obligatorio_y_no_trivial():
    with pytest.raises(ValidationError):
        schemas.ConsultaCreate(
            subject={"nombre": "Juan", "ape_paterno": "Perez"},
            requested_by="ana",
            motivo="corto",  # < 10 chars => rechazado
            year_from=2020,
            year_to=2021,
        )


def test_consulta_valida():
    c = schemas.ConsultaCreate(
        subject={"nombre": "Juan", "ape_paterno": "Perez", "ape_materno": "Soto"},
        requested_by="ana",
        motivo="Debida diligencia de contratación",
        year_from=2020,
        year_to=2021,
    )
    assert c.motivo
    assert c.competencias  # default: Civil/Laboral/Penal/Cobranza


def test_rango_anios_invalido():
    with pytest.raises(ValidationError):
        schemas.ConsultaCreate(
            subject={"nombre": "Juan", "ape_paterno": "Perez"},
            requested_by="ana",
            motivo="Debida diligencia laboral previa",
            year_from=2022,
            year_to=2020,
        )


def test_competencia_invalida():
    with pytest.raises(ValidationError):
        schemas.ConsultaCreate(
            subject={"nombre": "Juan", "ape_paterno": "Perez"},
            requested_by="ana",
            motivo="Debida diligencia laboral previa",
            competencias=["Marciano"],
            year_from=2020,
            year_to=2021,
        )
