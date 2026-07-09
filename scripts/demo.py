#!/usr/bin/env python3
"""Smoke/demo del stack (T-86): crea una consulta → espera `done` → muestra el informe.

Corre desde el host contra la API (sólo stdlib). Con el stack en modo mock (default)
devuelve datos demostrativos; en modo real, la consulta real.

    docker compose up -d           # stack (mock por defecto)
    python scripts/demo.py         # crea, espera y muestra el informe
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request


def _req(method: str, url: str, api_key: str | None, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "null")


def main() -> int:
    ap = argparse.ArgumentParser(description="Demo/smoke del stack Chapi Local")
    ap.add_argument("--base-url", default=os.getenv("BASE_URL", "http://localhost:8000"))
    ap.add_argument("--api-key", default=os.getenv("API_KEY") or None)
    ap.add_argument("--nombre", default="Ana")
    ap.add_argument("--ape-paterno", default="Diaz")
    ap.add_argument("--ape-materno", default="Soto")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()
    base = args.base_url.rstrip("/")

    payload = {
        "subject": {"nombre": args.nombre, "ape_paterno": args.ape_paterno,
                    "ape_materno": args.ape_materno},
        "requested_by": "demo",
        "motivo": "Demostración de due diligence previa a contratación",
        "competencias": ["Civil", "Penal"], "year_from": 2019, "year_to": 2021,
    }
    st, created = _req("POST", f"{base}/consultas", args.api_key, payload)
    if st != 202:
        print(f"❌ No se pudo crear la consulta (HTTP {st}): {created}")
        return 1
    cid = created["id"]
    print(f"[creada] {cid} · estado={created['status']}")

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        st, d = _req("GET", f"{base}/consultas/{cid}", args.api_key)
        if st == 200 and d["status"] in ("done", "error"):
            break
        time.sleep(2)
    else:
        print("⏱️  Timeout esperando `done`.")
        return 2

    if d["status"] == "error":
        print(f"❌ Consulta en error: {d.get('error')}")
        return 1

    print(f"[done] causas: {len(d.get('cases', []))} · nivel: {d.get('risk_level')} · "
          f"score: {d.get('risk_score')} · homónimos: {d.get('homonym_count')}")
    print(f"Informe:  {base}/consultas/{cid}/report")
    print(f"PDF:      {base}/consultas/{cid}/report.pdf  (requiere navegador)")
    print(f"UI:       {base}/ui/consultas/{cid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
