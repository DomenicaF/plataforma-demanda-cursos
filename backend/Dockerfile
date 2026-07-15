FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema mínimas para compilar ruedas si hiciera falta
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Inicializa la BD (usuarios y fuentes por defecto) y arranca la API
CMD ["sh", "-c", "python -m scripts.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
