#!/usr/bin/env python3
"""
Test RunPod Worker pour VideoAI Studio
Simule la génération de vidéo sans GPU pour tester l'intégration
"""

import runpod
from runpod.serverless.utils.rp_validator import validate
import uuid
import time  # Pour timestamp dans l'ID


def handler(job):
    """
    Handler de test pour VideoAI Studio
    Simule la génération de vidéo sans utiliser de GPU
    """
    print(f"🎬 Job reçu: {job.get('id', 'local-test')}")
    
    # Définir le schéma de validation
    schema = {
        "prompt": {
            "type": str,
            "required": True,
            "constraints": lambda x: len(x.strip()) > 0 and len(x) <= 500  # Non vide et max 500 caractères
        }
    }
    
    # Valider l'input
    job_input = job.get('input', {})
    validated_input = validate(job_input, schema)
    
    # Vérifier les erreurs de validation
    if "errors" in validated_input:
        return {
            "error": f"Validation failed: {validated_input['errors']}",
            "status": "failed"
        }
    
    # Récupérer le prompt validé
    prompt = validated_input["validated_input"]["prompt"]
    
    print(f"📝 Prompt: {prompt}")
    
    # Générer un ID unique pour la vidéo
    video_id = f"test_{uuid.uuid4().hex[:8]}_{int(time.time())}"
    
    # Simuler une URL de stockage (comme si c'était uploadé)
    video_url = f"https://storage.runpod.io/test-videos/{video_id}.mp4"
    
    # Résultat simplifié - juste l'essentiel pour le test
    result = {
        "video_url": video_url,
        "prompt": prompt
    }
    
    print(f"\n Génération terminée avec succès!")
    print(f"URL de la vidéo: {video_url}")
    
    return result


# Point d'entrée RunPod
if __name__ == "__main__":
    print("=" * 50)
    print("Test RunPod Worker")
    print("=" * 50)
    
    runpod.serverless.start({"handler": handler})