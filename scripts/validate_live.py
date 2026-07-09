#!/usr/bin/env python3
"""Driver de validación EN VIVO del scraper real (T-200 / T-205).

Crea una consulta ACOTADA (por defecto 1 competencia y 1 año, para no golpear la
fuente), hace polling del estado y reporta causas/score, señalando dónde quedaron
el JSON por persona y el informe. Sólo usa la stdlib (urllib/json).

Prerequisito: el stack corriendo en modo vivo, p.ej.:
    docker compose -f docker-compose.yml -f docker-compose.live.yml up --build

Ejemplos:
    python scripts/validate_live.py --nombre "SERGIO ANDRES" \
        --ape-paterno COVARRUBIAS --ape-materno VALENZUELA \
        --competencia Penal --year 2011
    # Verificar Civil/Cobranza (T-200):
    python scripts/validate_live.py --nombre JUAN --ape-paterno PEREZ \
        --competencia Civil --year 2020
"""
from __future__ import annotations

import argparse
import json
import os
import sys
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
    ap = argparse.ArgumentParser(description="Validación en vivo del scraper real")
    ap.add_argument("--base-url", default=os.getenv("BASE_URL", "http://localhost:8000"))
    ap.add_argument("--api-key", default=os.getenv("API_KEY") or None)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--ape-paterno", default="")
    ap.add_argument("--ape-materno", default="")
    ap.add_argument("--competencia", default="Penal",
                    choices=["Civil", "Laboral", "Penal", "Cobranza"])
    ap.add_argument("--year", type=int, default=2011)
    ap.add_argument("--motivo", default="Validacion tecnica del scraper en vivo")
    ap.add_argument("--timeout", type=int, default=1800, help="segundos máx. de espera")
    ap.add_argument("--poll", type=float, default=5.0, help="intervalo de polling (s)")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")

    # 0) Readiness
    st, ready = _req("GET", f"{base}/health/ready", args.api_key)
    print(f"[readiness] HTTP {st}: {ready}")
    if st != 200:
        print("⚠️  El stack no está listo (DB/Redis). Continúo igualmente.", file=sys.stderr)

    # 1) Crear consulta acotada
    payload = {
        "subject": {
            "nombre": args.nombre,
            "ape_paterno": args.ape_paterno,
            "ape_materno": args.ape_materno,
        },
        "requested_by": "validacion-en-vivo",
        "motivo": args.motivo,
        "competencias": [args.competencia],
        "year_from": args.year,
        "year_to": args.year,
    }
    st, created = _req("POST", f"{base}/consultas", args.api_key, payload)
    if st != 202:
        print(f"❌ No se pudo crear la consulta (HTTP {st}): {created}", file=sys.stderr)
        return 1
    cid = created["id"]
    print(f"[creada] consulta {cid} · {args.competencia} {args.year} · estado={created['status']}")

    # 2) Polling hasta done/error/timeout
    deadline = time.time() + args.timeout
    last = None
    while time.time() < deadline:
        st, detail = _req("GET", f"{base}/consultas/{cid}", args.api_key)
        if st != 200:
            print(f"❌ Error consultando estado (HTTP {st}): {detail}", file=sys.stderr)
            return 1
        status = detail["status"]
        if status != last:
            print(f"[estado] {status}")
            last = status
        if status in ("done", "error"):
            break
        time.sleep(args.poll)
    else:
        print(f"⏱️  Timeout tras {args.timeout}s; última vez estado={last}", file=sys.stderr)
        return 2

    # 3) Reporte
    if detail["status"] == "error":
        print(f"❌ Consulta en error: {detail.get('error')}", file=sys.stderr)
        return 1

    cases = detail.get("cases", [])
    print("\n===== RESULTADO =====")
    print(f"causas: {len(cases)} · nivel: {detail.get('risk_level')} · "
          f"score: {detail.get('risk_score')} · homónimos: {detail.get('homonym_count')}")
    print(f"conteos por competencia: {detail.get('counts')}")
    for c in cases[:5]:
        lit = len(c.get("litigantes") or [])
        rel = len(c.get("relaciones") or [])
        print(f"  - {c.get('competencia')} {c.get('rit')} · {c.get('tribunal')} · "
              f"{c.get('estado')} · litigantes={lit} relaciones={rel}")
    if len(cases) > 5:
        print(f"  … y {len(cases) - 5} más")
    print(f"\nJSON por persona en el volumen ./results/ · informe: {base}/consultas/{cid}/report")
    print(f"auditoría: {base}/audit?consulta_id={cid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
