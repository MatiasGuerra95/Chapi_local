"""T-223: consulta de empresas (razón social/RUT)."""
import pytest
from pydantic import ValidationError

from app import schemas


def _consulta(subject: dict):
    return schemas.ConsultaCreate(
        subject=subject,
        requested_by="ana",
        motivo="Debida diligencia de proveedor",
        competencias=["Civil"],
        year_from=2020,
        year_to=2021,
    )


def test_empresa_valida_deriva_nombre_de_razon_social():
    c = _consulta({"tipo": "empresa", "razon_social": "Constructora Andes SpA", "rut": "76.111.222-3"})
    assert c.subject.tipo == "empresa"
    # El flujo de búsqueda usa 'nombre': se completa con la razón social.
    assert c.subject.nombre == "Constructora Andes SpA"


def test_empresa_respeta_nombre_explicito():
    c = _consulta({"tipo": "empresa", "razon_social": "Comercial Sur Ltda", "nombre": "COMERCIAL SUR"})
    assert c.subject.nombre == "COMERCIAL SUR"


def test_empresa_sin_razon_social_rechazada():
    with pytest.raises(ValidationError):
        _consulta({"tipo": "empresa", "rut": "76.111.222-3"})


def test_persona_sin_nombre_rechazada():
    with pytest.raises(ValidationError):
        _consulta({"tipo": "persona", "ape_paterno": "Perez"})


def test_tipo_invalido_rechazado():
    with pytest.raises(ValidationError):
        _consulta({"tipo": "marciano", "nombre": "X"})


def test_persona_sigue_funcionando():
    c = _consulta({"nombre": "Juan", "ape_paterno": "Perez", "ape_materno": "Soto"})
    assert c.subject.tipo == "persona"
    assert c.subject.nombre == "Juan"
