"""
crawler_nom.py  ·  Piloto PJUD — Búsqueda por Nombre (v6-patience)
------------------------------------------------------------------
• Ahora espera hasta 45 s por resultados de tabla antes de saltar.
• Recorre competencia Penal · año 2011 · todas las Cortes/Tribunales.
• Para cada causa guarda fila + Detalle (litigantes, relaciones).
• DEBUG=True → ventana visible + slow-mo; False → headless.
"""
import asyncio, json, random
from pathlib import Path
from typing import Dict, List

from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
from slugify import slugify

# ─── Config ───────────────────────────────────────────────────────────────
BASE               = "https://oficinajudicialvirtual.pjud.cl"
RESULT_DIR         = Path("results")
COMPETENCIAS       = {"Penal": "5"}
YEAR_FROM, YEAR_TO = 2011, 2011
DEBUG              = True
SLOW_MO_MS         = 250 if DEBUG else 0
RESULT_DIR.mkdir(exist_ok=True, parents=True)

# ─── Utilidades ------------------------------------------------------------
def slug(nombre: str, ape_p: str, ape_m: str) -> str:
    return slugify(f"{nombre}_{ape_p}_{ape_m}")

def text(td):
    return td.get_text(strip=True)

def parse_litigantes(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("#litigantesPen tbody tr")
    out = []
    for tr in rows:
        t = [text(td) for td in tr("td")]
        if t: out.append({"tipo": t[0], "nombre": t[1], "situacion": t[2]})
    return out

def parse_relaciones(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("#relacionesPen tbody tr")
    out = []
    for tr in rows:
        t = [text(td) for td in tr("td")]
        if t:
            out.append(
                {"nombre": t[0], "delito": t[1], "estado": t[2], "fec_estado": t[3]}
            )
    return out

async def abrir_consulta(page: Page) -> Page:
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

# –– NUEVO: espera paciente a filas válidas ––––––––––––––––––––––––––––––––
async def wait_tabla(page: Page, timeout_ms: int = 15000) -> bool:
    """Devuelve True si encuentra al menos 1 fila con ≥7 celdas dentro del plazo."""
    step = 1500
    elapsed = 0
    while elapsed < timeout_ms:
        filas = await page.query_selector_all("#dtaTableDetalleNombre tbody tr")
        for tr in filas:
            if len(await tr.query_selector_all("td")) >= 7:
                return True
        await asyncio.sleep(step / 1000)
        elapsed += step
    return False

# ─── Scraper principal ────────────────────────────────────────────────────
async def scan_persona(nombre: str, ape_p: str, ape_m: str):
    out_json = RESULT_DIR / f"{slug(nombre, ape_p, ape_m)}.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not DEBUG, slow_mo=SLOW_MO_MS)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(f"{BASE}/home/index.php")
        page = await abrir_consulta(page)

        with out_json.open("w", encoding="utf-8") as jf:
            jf.write("[\n")

        for comp_nom, comp_val in COMPETENCIAS.items():
            await page.select_option("#nomCompetencia", comp_val)
            await page.select_option("#corteNom", "0")
            await page.wait_for_selector("#nomTribunal")
            tribunales = await page.eval_on_selector_all(
                "#nomTribunal option", "opts=>opts.map(o=>o.value).filter(v=>v&&v!=='0')"
            )

            for trib_val in tribunales:
                await page.select_option("#nomTribunal", trib_val)
                await page.fill("#nomNombre", nombre)
                await page.fill("#nomApePaterno", ape_p)
                await page.fill("#nomApeMaterno", ape_m)

                for yr in range(YEAR_FROM, YEAR_TO + 1):
                    await page.fill("#nomEra", str(yr))
                    await page.click("#btnConConsultaNom")

                    if not await wait_tabla(page):           # ← usa la espera paciente
                        if DEBUG:
                            print(f"⏳ 0 filas ▸ {trib_val=} {yr=}")
                        continue

                    filas = await page.query_selector_all("#dtaTableDetalleNombre tbody tr")
                    for tr in filas:
                        tds = await tr.query_selector_all("td")
                        if len(tds) < 7:
                            continue

                        fila = dict(
                            rit=await tds[1].inner_text(),
                            tribunal=await tds[2].inner_text(),
                            ruc=await tds[3].inner_text(),
                            carat=await tds[4].inner_text(),
                            fec_ing=await tds[5].inner_text(),
                            estado=await tds[6].inner_text(),
                            competencia=comp_nom,
                            tribunal_id=trib_val,
                            year=yr,
                        )

                        link = await tr.query_selector("a.toggle-modal")
                        if link:
                            await link.click()
                            await page.wait_for_selector(".modal.show", timeout=10000)
                            modal_html = await page.inner_html(".modal.show")
                            fila["litigantes"] = parse_litigantes(modal_html)
                            fila["relaciones"] = parse_relaciones(modal_html)
                            await page.keyboard.press("Escape")
                            await page.wait_for_selector(".modal.show", state="detached")

                        with out_json.open("a", encoding="utf-8") as jf:
                            json.dump(fila, jf, ensure_ascii=False)
                            jf.write(",\n")

                    await asyncio.sleep(random.uniform(0.4, 0.8))

        with out_json.open("ab+") as jf:
            jf.seek(-2, 2)
            jf.truncate()
            jf.write(b"\n]\n")

        await browser.close()

# ─── Demo ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(
        scan_persona(
            nombre="SERGIO ANDRÉS",
            ape_p="COVARRUBIAS",
            ape_m="VALENZUELA",
        )
    )
