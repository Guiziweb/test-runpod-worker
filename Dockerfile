# Dockerfile pour Test RunPod Worker
# Pas de GPU nécessaire pour ce worker de test

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="VideoAI Studio"
LABEL description="Test RunPod Worker pour génération vidéo simulée"

# Définir le répertoire de travail
WORKDIR /app

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    RUNPOD_DEBUG_LEVEL=INFO

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le handler
COPY handler.py .

# Copier les fichiers de test (optionnel, utile pour debug)
COPY test_input.json* ./

# Healthcheck pour vérifier que le container est prêt
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import runpod; print('OK')" || exit 1

# Commande de démarrage
CMD ["python", "-u", "handler.py"]