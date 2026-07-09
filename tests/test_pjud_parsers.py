"""T-201/T-202: parseo de litigantes/relaciones del modal de detalle por competencia.

Funciones puras (BeautifulSoup) — no requieren navegador. Verifican el parseo y el
aislamiento por sufijo de competencia (#litigantes{Suf} / #relaciones{Suf}).
"""
from app.services.pjud_scraper import _parse_litigantes, _parse_relaciones

MODAL_PENAL = """
<div class="modal show">
  <table id="litigantesPen"><tbody>
    <tr><td>Imputado</td><td>JUAN PEREZ</td><td>Vigente</td></tr>
    <tr><td>Querellante</td><td>FISCALIA</td><td>Vigente</td></tr>
  </tbody></table>
  <table id="relacionesPen"><tbody>
    <tr><td>JUAN PEREZ</td><td>Hurto</td><td>En tramitacion</td><td>2020-01-15</td></tr>
  </tbody></table>
</div>
"""

MODAL_LABORAL = """
<div class="modal show">
  <table id="litigantesLab"><tbody>
    <tr><td>Demandante</td><td>ANA SOTO</td><td>Vigente</td></tr>
  </tbody></table>
</div>
"""


def test_parse_litigantes_penal():
    out = _parse_litigantes(MODAL_PENAL, "Pen")
    assert len(out) == 2
    assert out[0] == {"tipo": "Imputado", "nombre": "JUAN PEREZ", "situacion": "Vigente"}
    assert out[1]["nombre"] == "FISCALIA"


def test_parse_relaciones_penal():
    out = _parse_relaciones(MODAL_PENAL, "Pen")
    assert out == [
        {
            "nombre": "JUAN PEREZ",
            "delito": "Hurto",
            "estado": "En tramitacion",
            "fec_estado": "2020-01-15",
        }
    ]


def test_parse_litigantes_laboral():
    out = _parse_litigantes(MODAL_LABORAL, "Lab")
    assert out == [{"tipo": "Demandante", "nombre": "ANA SOTO", "situacion": "Vigente"}]


def test_sufijo_aisla_competencia():
    # El sufijo equivocado no debe cruzar tablas de otra competencia.
    assert _parse_litigantes(MODAL_PENAL, "Lab") == []
    assert _parse_relaciones(MODAL_LABORAL, "Pen") == []


def test_html_vacio_o_sin_tablas_devuelve_listas_vacias():
    assert _parse_litigantes("", "Pen") == []
    assert _parse_relaciones("<div>nada</div>", "Pen") == []


def test_celdas_faltantes_no_rompen():
    html = '<table id="litigantesPen"><tbody><tr><td>Solo tipo</td></tr></tbody></table>'
    out = _parse_litigantes(html, "Pen")
    assert out == [{"tipo": "Solo tipo", "nombre": "", "situacion": ""}]
