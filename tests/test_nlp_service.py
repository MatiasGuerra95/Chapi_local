"""T-210: síntesis narrativa (MockSummarizer) — útil y compatible con compliance."""
from app.config import settings
from app.services import nlp_service, risk_engine

_PROHIBIDOS = ("culpable", "contratar", "no contratar", "rechazar", "recomendamos")

_CASES = [
    {"competencia": "Penal", "estado": "En tramitación", "possible_homonym": True, "year": 2023},
    {"competencia": "Civil", "estado": "Terminada", "possible_homonym": True, "year": 2022},
]


def _risk():
    return risk_engine.compute_score(_CASES, current_year=2024)


def test_mock_resumen_no_vacio_y_menciona_revision():
    out = nlp_service.MockSummarizer().summarize(cases=_CASES, risk=_risk())
    assert out
    assert "revisión" in out.lower()
    assert "2 causa" in out  # total


def test_mock_resumen_sin_lenguaje_prohibido():
    out = nlp_service.MockSummarizer().summarize(cases=_CASES, risk=_risk()).lower()
    for p in _PROHIBIDOS:
        assert p not in out


def test_mock_resumen_sin_causas():
    risk = risk_engine.compute_score([], current_year=2024)
    out = nlp_service.MockSummarizer().summarize(cases=[], risk=risk)
    assert "No se identificaron causas" in out


def test_generate_summary_respeta_flag(monkeypatch):
    monkeypatch.setattr(settings, "enable_summary", False)
    assert nlp_service.generate_summary(_CASES, _risk()) == ""


def test_generate_summary_robusto_ante_error(monkeypatch):
    # Un summarizer que revienta no debe romper el informe.
    class Boom:
        def summarize(self, *, cases, risk):
            raise RuntimeError("modelo caído")

    monkeypatch.setattr(settings, "enable_summary", True)
    monkeypatch.setattr(nlp_service, "_summarizer", Boom())
    assert nlp_service.generate_summary(_CASES, _risk()) == ""


def test_informe_incluye_sintesis():
    from datetime import datetime
    from types import SimpleNamespace

    from app.services import report_generator

    risk = _risk()
    consulta = SimpleNamespace(
        requested_by="u", created_at=datetime(2024, 1, 1), status="done",
        motivo="Debida diligencia previa a contratación",
        params={"competencias": ["Penal", "Civil"], "year_from": 2022, "year_to": 2023})
    subject = SimpleNamespace(nombre="X", ape_paterno="Y", ape_materno="", rut=None)
    html = report_generator.render_report(
        consulta=consulta, subject=subject, cases=_CASES, risk=risk
    )
    assert "Síntesis (generada" in html
