from app.services import risk_engine


def test_empty_cases_low():
    r = risk_engine.compute_score([])
    assert r["level"] == "bajo"
    assert r["score"] == 0.0
    assert r["total"] == 0


def test_penal_pesa_mas_que_civil():
    civil = risk_engine.compute_score(
        [{"competencia": "Civil", "year": 2024, "estado": "Terminada", "possible_homonym": False}],
        current_year=2024,
    )
    penal = risk_engine.compute_score(
        [{"competencia": "Penal", "year": 2024, "estado": "En tramitación", "possible_homonym": False}],
        current_year=2024,
    )
    assert penal["score"] > civil["score"]


def test_homonym_warning_y_sin_recomendacion():
    r = risk_engine.compute_score(
        [{"competencia": "Penal", "year": 2024, "estado": "activa", "possible_homonym": True}],
        current_year=2024,
    )
    assert r["homonym_warning"] is True
    texto = " ".join(r["factors"]).lower()
    for prohibido in ("contratar", "no contratar", "culpable", "rechazar", "recomendamos"):
        assert prohibido not in texto


def test_niveles_por_score():
    # 4 causas penales recientes y activas -> nivel alto.
    cases = [
        {"competencia": "Penal", "year": 2024, "estado": "En tramitación", "possible_homonym": False}
        for _ in range(4)
    ]
    r = risk_engine.compute_score(cases, current_year=2024)
    assert r["level"] == "alto"
    assert r["counts"]["Penal"] == 4
