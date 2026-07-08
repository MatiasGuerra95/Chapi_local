"""T-87: informe (RC-03/RC-04) — el disclaimer niega culpabilidad/recomendación
y los indicadores no usan ese lenguaje. (No basta ausencia de palabras: el
disclaimer las menciona para negarlas.)"""
from datetime import datetime
from types import SimpleNamespace

from app.services import report_generator, risk_engine


def _render():
    cases = [
        {"competencia": "Penal", "rit": "P-1-2023", "tribunal": "T1", "caratulado": "X / Y",
         "fecha_ingreso": "2023-01-01", "estado": "En tramitación", "year": 2023,
         "possible_homonym": True},
        {"competencia": "Civil", "rit": "C-2-2022", "tribunal": "T2", "caratulado": "X / Z",
         "fecha_ingreso": "2022-05-01", "estado": "Terminada", "year": 2022,
         "possible_homonym": True},
    ]
    risk = risk_engine.compute_score(cases, current_year=2024)
    consulta = SimpleNamespace(
        requested_by="u", created_at=datetime(2024, 1, 1), status="done",
        motivo="Debida diligencia previa a contratación",
        params={"competencias": ["Penal", "Civil"], "year_from": 2022, "year_to": 2023})
    subject = SimpleNamespace(nombre="X", ape_paterno="Y", ape_materno="", rut=None)
    html = report_generator.render_report(consulta=consulta, subject=subject, cases=cases, risk=risk)
    return risk, html


def test_disclaimer_niega_culpabilidad_y_recomendacion():
    _, html = _render()
    assert "Disclaimer legal" in html
    assert "no constituyen una afirmación de culpabilidad" in html
    assert "contratar o no contratar" in html


def test_marca_homonimos_en_informe():
    _, html = _render()
    assert "posible homónimo" in html


def test_indicadores_sin_lenguaje_prohibido():
    risk, _ = _render()
    texto = " ".join(risk["factors"]).lower()
    for prohibido in ("culpable", "contratar", "no contratar", "rechazar", "recomendamos"):
        assert prohibido not in texto
