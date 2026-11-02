#!/usr/bin/env python3
"""Mapea el flujo de 'Ingreso como invitado' de la OJV (T-200/T-205).

Presiona 'Ingreso como invitado' (acceso sin Clave Única), sigue la navegación y
busca el formulario de 'Búsqueda por Nombre' (#nomNombre / #nomCompetencia) y la
presencia de reCAPTCHA. Guarda screenshots en results/. No resuelve captchas: sólo
mapea el flujo para decidir viabilidad.
"""
from __future__ import annotations

import asyncio

BASE = "https://oficinajudicialvirtual.pjud.cl"
FORM_SELECTORS = ["#nomNombre", "#nomApePaterno", "#nomCompetencia", "#nomTribunal",
                  "text=Búsqueda por Nombre", "text=Consulta causas"]
CAPTCHA_SELECTORS = ["iframe[src*='recaptcha']", ".g-recaptcha", ".grecaptcha-badge",
                     "iframe[title*='recaptcha']"]


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
    for sel in FORM_SELECTORS:
        try:
            el = await page.query_selector(sel)
            print(f"  form {sel!r:34}: {'PRESENTE' if el else 'ausente'}")
        except Exception as e:  # noqa: BLE001
            print(f"  form {sel!r:34}: error {str(e)[:40]}")
    hay_captcha = False
    for sel in CAPTCHA_SELECTORS:
        try:
            if await page.query_selector(sel):
                hay_captcha = True
                print(f"  reCAPTCHA detectado por {sel!r}")
        except Exception:  # noqa: BLE001
            pass
    if not hay_captcha:
        print("  reCAPTCHA: no detectado en esta página")


async def _newest(ctx, page):
    await asyncio.sleep(3)
    pages = ctx.pages
    print(f"\npáginas/tabs: {len(pages)}")
    for i, pg in enumerate(pages):
        print(f"  [{i}] {pg.url}")
    target = pages[-1]
    try:
        await target.wait_for_load_state("domcontentloaded", timeout=15000)
    except Exception:  # noqa: BLE001
        pass
    return target


async def _try_click(page, variants, label):
    for sel in variants:
        try:
            await page.click(sel, timeout=6000)
            print(f"\nclick {label} -> {sel!r} OK")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"click {label} {sel!r} falló: {str(e)[:70]}")
    return False


async def main() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(f"{BASE}/home/index.php", wait_until="domcontentloaded")

        # 1) Ingreso como invitado
        await _try_click(page, ["text=Ingreso como invitado", "text=Ingreso Como Invitado",
                                "text=Invitado"], "'Ingreso como invitado'")
        page = await _newest(ctx, page)
        await dump(page, "TRAS 'Ingreso como invitado'")
        try:
            await page.screenshot(path="/app/results/ojv_guest.png", full_page=True)
            print("screenshot -> results/ojv_guest.png")
        except Exception as e:  # noqa: BLE001
            print("screenshot err:", e)

        # 2) Si no vemos el formulario, intentar 'Consulta causas' / 'Búsqueda por Nombre'
        if not await page.query_selector("#nomNombre"):
            await _try_click(page, ["text=Búsqueda por Nombre", "text=Consulta causas",
                                    "text=Consulta Causas"], "'Consulta/Búsqueda'")
            page = await _newest(ctx, page)
            await dump(page, "TRAS 'Consulta/Búsqueda'")
            try:
                await page.screenshot(path="/app/results/ojv_search.png", full_page=True)
                print("screenshot -> results/ojv_search.png")
            except Exception as e:  # noqa: BLE001
                print("screenshot err:", e)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
