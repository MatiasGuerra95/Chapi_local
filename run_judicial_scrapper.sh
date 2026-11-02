#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
source entorno/bin/activate
cd judicial_records_scrapper
exec python main.py "$@"
