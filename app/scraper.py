from playwright.async_api import async_playwright

PJUD_URL = "https://ojv.pjud.cl/"

async def scrape_rut(rut: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(PJUD_URL)
        # TODO: login + búsqueda
        # ...
        await browser.close()
        return ["<html>dummy fallo</html>"]
