#!/usr/bin/env python3
"""Inspector de la OJV para T-200 (requiere Playwright + Chromium y sitio en vivo).

Vuelca los ``value``/label reales de ``#nomCompetencia`` para **confirmar** los
valores de Civil y Cobranza (Laboral=4 y Penal=5 ya están confirmados). Pensado
para ejecutarse dentro del contenedor del worker en modo vivo:

    docker compose -f docker-compose.yml -f docker-compose.live.yml \
        exec worker python /app/scripts/inspect_ojv.py

Con ``--tribunales`` también lista los tribunales de una competencia dada.
"""
from __future__ import annotations

import argparse
import asyncio

from app.services.pjud_scraper import PlaywrightPjudScraper, _abrir_consulta


async def run(competencia_val: str | None) -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(f"{PlaywrightPjudScraper.BASE}/home/index.php")
        page = await _abrir_consulta(page)

        opts = await page.eval_on_selector_all(
            "#nomCompetencia option",
            "os=>os.map(o=>({value:o.value,label:(o.textContent||'').trim()}))",
        )
        print("#nomCompetencia options (confirmar Civil/Cobranza — T-200):")
        for o in opts:
            print(f"  value={o['value']!r:>6}  label={o['label']!r}")

        if competencia_val:
            await page.select_option("#nomCompetencia", competencia_val)
            await page.select_option("#corteNom", "0")
            await page.wait_for_selector("#nomTribunal")
            tribs = await page.eval_on_selector_all(
                "#nomTribunal option",
                "os=>os.map(o=>({value:o.value,label:(o.textContent||'').trim()}))",
            )
            print(f"\n#nomTribunal para competencia value={competencia_val!r}:")
            for t in tribs[:20]:
                print(f"  value={t['value']!r:>6}  label={t['label']!r}")
            if len(tribs) > 20:
                print(f"  … y {len(tribs) - 20} más")

        await browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Inspector de la OJV (T-200)")
    ap.add_argument("--tribunales", metavar="COMP_VALUE",
                    help="value de #nomCompetencia para listar sus tribunales")
    args = ap.parse_args()
    asyncio.run(run(args.tribunales))


if __name__ == "__main__":
    main()
