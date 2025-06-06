FROM python:3.12-slim

# Dependencias del sistema (Playwright + llama.cpp)
RUN apt-get update \
 && apt-get install -y curl wget git libgl1-mesa-glx libglib2.0-0 libxcb-xinerama0 \
 && apt-get clean

# Playwright drivers
RUN pip install --no-cache-dir playwright==1.43.* && playwright install --with-deps chromium

# Python deps
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar código
WORKDIR /app
COPY app /app/app
COPY .env.sample /app/.env

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
