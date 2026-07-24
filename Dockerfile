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
CMD ["python", "-c", "print('SensusVault Engine Ready')"]