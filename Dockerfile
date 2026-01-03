# Wir nehmen ein leichtes Python-Image
FROM python:3.10-slim

# Arbeitsordner im Container erstellen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den Rest des Codes kopieren
COPY .venv .

# Den Bot starten
CMD ["python", "Main.py"]