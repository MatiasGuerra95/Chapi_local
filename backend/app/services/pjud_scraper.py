"""Interfaz de scraping del Poder Judicial + implementación mock y skeleton Playwright.

El scraper es un *productor puro*: expone ``scan_persona`` como async generator que
emite ``CaseRecord``. El worker consume el generador, escribe JSON en tiempo real y
persiste en Postgres. Así el mock se reemplaza por Playwright sin tocar el worker.
"""
from __future__ import annotations

import asyncio
import hashlib
import re
from typing import AsyncIterator, Protocol, TypedDict, runtime_checkable

from app.config import COMPETENCIAS, settings
from app.services.throttle import RateLimiter


class CaseRecord(TypedDict, total=False):
    competencia: str
    rit: str
    ruc: str
    tribunal: str
    caratulado: str
    fecha_ingreso: str
    estado: str
    year: int
    litigantes: list[dict]
    relaciones: list[dict]
    possible_homonym: bool
    source_url: str


@runtime_checkable
class PjudScraper(Protocol):
    def scan_persona(
        self,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        competencias: list[str],
        year_from: int,
        year_to: int,
    ) -> AsyncIterator[CaseRecord]:
        ...


def persona_slug(nombre: str, ape_paterno: str, ape_materno: str) -> str:
    """Slug estable para nombrar el JSON por persona (con fallback sin dependencias)."""
    raw = f"{nombre}_{ape_paterno}_{ape_materno}"
    try:
        from slugify import slugify

        return slugify(raw) or "consulta"
    except Exception:
        return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-") or "consulta"


def _count(comp: str, year: int) -> int:
    """Número determinista de causas (0-2) por competencia/año para el mock."""
    return int(hashlib.md5(f"{comp}-{year}".encode()).hexdigest(), 16) % 3


class MockPjudScraper:
    """Scraper mockeado: datos deterministas, incluye homónimos demostrativos."""

    async def scan_persona(
        self,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        competencias: list[str],
        year_from: int,
        year_to: int,
    ) -> AsyncIterator[CaseRecord]:
        full = " ".join(x for x in (nombre, ape_paterno, ape_materno) if x).strip()
        comps = list(competencias) or ["Civil"]
        demo_comp = comps[0]

        # Homónimos demostrativos: mismo nombre, distinto RUT y tribunal.
        for i, rut in enumerate(("12.345.678-9", "9.876.543-2"), start=1):
            yield {
                "competencia": demo_comp,
                "rit": f"{demo_comp[0]}-{i}-{year_from}",
                "ruc": f"{year_from}{i:07d}-K",
                "tribunal": f"Tribunal Demostrativo {i}",
                "caratulado": f"{full.title()} / Contraparte {i}",
                "fecha_ingreso": f"{year_from}-03-1{i}",
                "estado": "En tramitación" if i == 1 else "Terminada",
                "year": year_from,
                "litigantes": [
                    {"tipo": "Demandado", "nombre": full.upper(), "rut": rut, "situacion": "Vigente"}
                ],
                "relaciones": [],
                "possible_homonym": True,
                "source_url": "mock://ojv.pjud.cl/consulta-por-nombre",
            }
            await asyncio.sleep(0.01)

        # Variedad determinista por competencia y año.
        seq = 0
        for comp in comps:
            for year in range(year_from, year_to + 1):
                for _ in range(_count(comp, year)):
                    seq += 1
                    rut_fake = f"{10_000_000 + (seq * 37) % 89_999_999}-{seq % 10}"
                    yield {
                        "competencia": comp,
                        "rit": f"{comp[0]}-{100 + seq}-{year}",
                        "ruc": f"{year}{seq:07d}-{seq % 9}",
                        "tribunal": f"Tribunal Demo {1 + (seq % 4)}",
                        "caratulado": f"{full.title()} / Contraparte {seq}",
                        "fecha_ingreso": f"{year}-0{1 + (seq % 9)}-15",
                        "estado": "Terminada" if seq % 2 else "En tramitación",
                        "year": year,
                        "litigantes": [
                            {
                                "tipo": "Demandado",
                                "nombre": full.upper(),
                                "rut": rut_fake,
                                "situacion": "Vigente",
                            }
                        ],
                        "relaciones": [],
                        "possible_homonym": True,  # búsqueda por nombre => posible homónimo
                        "source_url": "mock://ojv.pjud.cl/consulta-por-nombre",
                    }
                    await asyncio.sleep(0.01)


# ─── Skeleton Playwright (fase 2) ──────────────────────────────────────────
# Portado de crawler_nom.py. Se activa con USE_MOCK_SCRAPER=false. Las partes
# dependientes del DOM vivo de la OJV quedan marcadas con TODO.

def _text(td) -> str:
    return td.get_text(strip=True)


def _parse_litigantes(html: str, comp_suffix: str = "Pen") -> list[dict]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    out = []
    for tr in soup.select(f"#litigantes{comp_suffix} tbody tr"):
        t = [_text(td) for td in tr("td")]
        if t:
            out.append({"tipo": t[0], "nombre": t[1] if len(t) > 1 else "", "situacion": t[2] if len(t) > 2 else ""})
    return out


def _parse_relaciones(html: str, comp_suffix: str = "Pen") -> list[dict]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    out = []
    for tr in soup.select(f"#relaciones{comp_suffix} tbody tr"):
        t = [_text(td) for td in tr("td")]
        if t:
            out.append(
                {
                    "nombre": t[0],
                    "delito": t[1] if len(t) > 1 else "",
                    "estado": t[2] if len(t) > 2 else "",
                    "fec_estado": t[3] if len(t) > 3 else "",
                }
            )
    return out


async def _abrir_consulta(page):
    """Abre 'Consulta causas' -> 'Búsqueda por Nombre' (portado de crawler_nom.py)."""
    pages_before = page.context.pages
    await page.click("text=Consulta causas")
    await asyncio.sleep(1)
    pages_now = page.context.pages
    if len(pages_now) > len(pages_before):
        page = pages_now[-1]
        await page.wait_for_load_state()
    await page.click("text=Búsqueda por Nombre")
    await page.wait_for_selector("#nomNombre")
    return page


async def _wait_tabla(page, timeout_ms: int = 15000) -> bool:
    """True si aparece al menos 1 fila con >=7 celdas dentro del plazo."""
    step, elapsed = 1500, 0
    while elapsed < timeout_ms:
        filas = await page.query_selector_all("#dtaTableDetalleNombre tbody tr")
        for tr in filas:
            if len(await tr.query_selector_all("td")) >= 7:
                return True
        await asyncio.sleep(step / 1000)
        elapsed += step
    return False


class PlaywrightPjudScraper:
    """Scraper real (skeleton) contra la OJV. Reemplaza al mock en fase 2."""

    BASE = "https://oficinajudicialvirtual.pjud.cl"

    def __init__(self, debug: bool = False):
        self.debug = debug
        # Politeness hacia la OJV (T-104): intervalo mínimo + jitter entre búsquedas.
        self._limiter = RateLimiter(
            settings.scraper_min_delay_seconds, settings.scraper_jitter_seconds
        )

    async def scan_persona(
        self,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        competencias: list[str],
        year_from: int,
        year_to: int,
    ) -> AsyncIterator[CaseRecord]:
        from playwright.async_api import async_playwright  # import perezoso

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=not self.debug)
            ctx = await browser.new_context()
            page = await ctx.new_page()
            await page.goto(f"{self.BASE}/home/index.php")
            page = await _abrir_consulta(page)

            for comp_nom in competencias:
                comp_val = COMPETENCIAS.get(comp_nom)
                if not comp_val:
                    continue
                # TODO(fase-2): verificar value real de Civil/Cobranza en #nomCompetencia.
                await page.select_option("#nomCompetencia", comp_val)
                await page.select_option("#corteNom", "0")
                await page.wait_for_selector("#nomTribunal")
                tribunales = await page.eval_on_selector_all(
                    "#nomTribunal option",
                    "opts=>opts.map(o=>o.value).filter(v=>v&&v!=='0')",
                )

                for trib_val in tribunales:
                    await page.select_option("#nomTribunal", trib_val)
                    await page.fill("#nomNombre", nombre)
                    await page.fill("#nomApePaterno", ape_paterno)
                    await page.fill("#nomApeMaterno", ape_materno)

                    for yr in range(year_from, year_to + 1):
                        await page.fill("#nomEra", str(yr))
                        # Politeness: respeta el intervalo mínimo antes de cada búsqueda.
                        await self._limiter.acquire()
                        await page.click("#btnConConsultaNom")
                        if not await _wait_tabla(page):
                            continue

                        filas = await page.query_selector_all(
                            "#dtaTableDetalleNombre tbody tr"
                        )
                        for tr in filas:
                            tds = await tr.query_selector_all("td")
                            if len(tds) < 7:
                                continue
                            rec: CaseRecord = {
                                "competencia": comp_nom,
                                "rit": await tds[1].inner_text(),
                                "tribunal": await tds[2].inner_text(),
                                "ruc": await tds[3].inner_text(),
                                "caratulado": await tds[4].inner_text(),
                                "fecha_ingreso": await tds[5].inner_text(),
                                "estado": await tds[6].inner_text(),
                                "year": yr,
                                "litigantes": [],
                                "relaciones": [],
                                # Búsqueda por nombre => marcar posible homónimo hasta
                                # confirmar por RUT.
                                "possible_homonym": True,
                                "source_url": f"{self.BASE}/",
                            }
                            # TODO(fase-2): abrir modal de detalle por competencia y
                            # poblar litigantes/relaciones con _parse_litigantes/_parse_relaciones.
                            yield rec

            await browser.close()


def get_scraper() -> PjudScraper:
    """Factory: mock por defecto, Playwright cuando USE_MOCK_SCRAPER=false."""
    if settings.use_mock_scraper:
        return MockPjudScraper()
    return PlaywrightPjudScraper()
