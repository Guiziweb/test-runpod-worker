# Test RunPod Worker - VideoAI Studio

Worker de test pour valider l'intégration RunPod ↔ Symfony sans utiliser de GPU.

Ce worker simule la génération de vidéo pour :
- Tester l'intégration sans coûts GPU
- Valider le workflow GitHub → RunPod

##  Quick Start

### 1. Installation locale

```bash
# Cloner le repo
git clone https://github.com/guiziweb/test-runpod-worker.git
cd test-runpod-worker

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  
# Installer dépendances
pip install -r requirements.txt
```

### 3. Serveur API local (simule RunPod)

```bash
# Démarrer le serveur
python handler.py --rp_serve_api --rp_api_port 8003

# Dans un autre terminal, tester avec curl
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Ma vidéo test", "duration": 5}}'
```