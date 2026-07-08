import asyncio

from app.services.pjud_scraper import MockPjudScraper, get_scraper, persona_slug


def _collect(**kwargs):
    async def run():
        scraper = MockPjudScraper()
        return [rec async for rec in scraper.scan_persona(**kwargs)]

    return asyncio.run(run())


def test_mock_emite_causas_con_homonimo():
    recs = _collect(
        nombre="JUAN",
        ape_paterno="PEREZ",
        ape_materno="SOTO",
        competencias=["Penal", "Civil"],
        year_from=2020,
        year_to=2022,
    )
    assert len(recs) >= 2
    assert all("competencia" in r for r in recs)
    assert any(r["possible_homonym"] for r in recs)
    # Homónimos demostrativos: mismo nombre, distinto RUT.
    ruts = {r["litigantes"][0]["rut"] for r in recs if r.get("litigantes")}
    assert len(ruts) >= 2


def test_mock_es_determinista():
    kwargs = dict(
        nombre="ANA",
        ape_paterno="DIAZ",
        ape_materno="",
        competencias=["Laboral"],
        year_from=2019,
        year_to=2021,
    )
    assert len(_collect(**kwargs)) == len(_collect(**kwargs))


def test_get_scraper_default_mock():
    assert isinstance(get_scraper(), MockPjudScraper)


def test_persona_slug():
    assert persona_slug("Juan", "Pérez", "Soto") == "juan-perez-soto"
