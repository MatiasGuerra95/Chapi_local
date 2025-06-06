from fastapi import FastAPI
from app.scraper import scrape_rut
from app.nlp_service import summarize_case

app = FastAPI(title="Chapi Local")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/rut/{rut}")
async def get_rut(rut: str):
    html_cases = await scrape_rut(rut)
    summary = [summarize_case(c) for c in html_cases]
    return {"rut": rut, "cases": summary}
