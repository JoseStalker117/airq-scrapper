FROM python:3.11-slim

WORKDIR /cronos

# Copiar archivos
COPY . .

# Evitar errores con debconf
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias para Chromium + Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libgtk-3-0 \
    libgbm1 \
    libxshmfence1 \
    libxss1 \
    libappindicator3-1 \
    libatspi2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores de Playwright
RUN python -m playwright install --with-deps

# Asegura que los logs se vean en tiempo real
ENV PYTHONUNBUFFERED=1

CMD ["python", "cronos.py"]
