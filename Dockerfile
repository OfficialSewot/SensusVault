FROM python:3.12-slim

WORKDIR /app

# Fix für Netzwerk/Repository-Probleme bei apt-get update
RUN apt-get update && apt-get upgrade -y

# Installiere System Dependencies (korrigierte libgl1 Versionen)
RUN apt-get install -y \
    build-essential \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installiere Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Code
COPY . .

# Startbefehl
ENV APP_PORT=2200
CMD ["sh", "-c", "python -m uvicorn src.api.main:app --host 0.0.0.0 --port ${APP_PORT}"]
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8