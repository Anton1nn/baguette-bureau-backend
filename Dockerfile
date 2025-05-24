FROM python:3.11-slim

# Crée un dossier dans le conteneur
WORKDIR /app

# Copie tout le code actuel dans le conteneur
COPY . .

# Installe les dépendances
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev build-essential

# Met à jour pip
RUN pip install --upgrade pip

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port 8000 pour l'API FastAPI
EXPOSE 8000

# Lance le serveur FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
