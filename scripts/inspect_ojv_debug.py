#!/usr/bin/env python3
"""Diagnóstico del DOM vivo de la OJV cuando la navegación falla (T-200/T-205).

Vuelca los textos clicables y la presencia de selectores en la home y tras pulsar
"Consulta causas", y guarda un screenshot en results/ojv_debug.png. No depende de
`_abrir_consulta` (que es justo lo que estamos depurando).
"""
from __future__ import annotations

import asyncio

BASE = "https://oficinajudicialvirtual.pjud.cl"
SELECTORS = [
    "#nomNombre", "#nomCompetencia", "#nomTribunal", "#nomApePaterno",
    "text=Búsqueda por Nombre", "text=Consulta causas", "text=Consulta Causas",
    "text=Clave Única", "text=Clave Unica", "text=Ingresar",
]


async def dump(page, label: str) -> None:
    print(f"\n===== {label} =====")
    print("url  :", page.url)
    try:
        print("title:", await page.title())
    except Exception as e:  # noqa: BLE001
        print("title: (err)", e)
    try:
        textos = await page.eval_on_selector_all(
            "a, button, li[role=tab], .nav-link, [onclick]",
            "els=>els.map(e=>(e.textContent||'').replace(/\\s+/g,' ').trim())"
            ".filter(t=>t && t.length>0 && t.length<70)",
        )
    except Exception as e:  # noqa: BLE001
        textos = []
        print("clicables: (err)", e)
    vistos = []
    for t in textos:
        if t not in vistos:
            vistos.append(t)
    print(f"clicables ({len(vistos)}):")
    for t in vistos[:70]:
        print("   -", t)
    for sel in SELECTORS:
        try:
            el = await page.query_selector(sel)
            print(f"  selector {sel!r:42}: {'PRESENTE' if el else 'ausente'}")
        except Exception as e:  # noqa: BLE001
            print(f"  selector {sel!r:42}: error {str(e)[:50]}")


async def main() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(f"{BASE}/home/index.php", wait_until="domcontentloaded")
        await dump(page, "HOME")

        clicked = None
        for sel in ["text=Consulta causas", "text=Consulta Causas", "text=Consulta de Causas"]:
            try:
                await page.click(sel, timeout=5000)
                clicked = sel
                break
            except Exception as e:  # noqa: BLE001
                print(f"\nclick {sel!r} falló: {str(e)[:80]}")
        print(f"\nclick 'Consulta causas' -> {clicked!r}")
        await asyncio.sleep(3)

        pages = ctx.pages
        print(f"\npáginas/tabs abiertas: {len(pages)}")
        for i, pg in enumerate(pages):
            print(f"  [{i}] {pg.url}")

        target = pages[-1]
        try:
            await target.wait_for_load_state("domcontentloaded")
        except Exception:  # noqa: BLE001
            pass
        await dump(target, "TRAS 'Consulta causas'")

        try:
            await target.screenshot(path="/app/results/ojv_debug.png", full_page=True)
            print("\nscreenshot -> results/ojv_debug.png (en el host)")
        except Exception as e:  # noqa: BLE001
            print("\nscreenshot err:", e)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
