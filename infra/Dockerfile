FROM python:3.12-slim

# Dependencias del sistema para Playwright/Chromium
RUN apt-get update \
 && apt-get install -y curl wget git libgl1-mesa-glx libglib2.0-0 libxcb-xinerama0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Drivers de Playwright (Chromium)
RUN pip install --no-cache-dir playwright==1.43.* && playwright install --with-deps chromium

# Dependencias Python (MVP; el stack ML de fase 2 va en requirements-ml.txt)
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY backend /app/backend
COPY workers /app/workers

ENV PYTHONPATH=/app/backend:/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
# La API usa este CMD; el worker sobreescribe command en docker-compose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
