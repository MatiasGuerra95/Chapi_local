FROM python:3.12-slim

# Dependencias del sistema base
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl wget git libgl1 libglib2.0-0 libxcb-xinerama0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Dependencias Python (MVP; el stack ML de fase 2 va en requirements-ml.txt)
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Navegador de Playwright: descarga pesada, sólo para el scraper real (fase 2).
#   docker compose build --build-arg INSTALL_BROWSERS=true
ARG INSTALL_BROWSERS=false
RUN if [ "$INSTALL_BROWSERS" = "true" ]; then playwright install --with-deps chromium; fi

WORKDIR /app
COPY backend /app/backend
COPY workers /app/workers

ENV PYTHONPATH=/app/backend:/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
# La API usa este CMD; el worker sobreescribe command en docker-compose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
