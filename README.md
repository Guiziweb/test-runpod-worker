# WAN 2.1 RunPod Worker

Worker RunPod qui génère des vidéos avec **WAN 2.1 T2V-1.3B**.

## Build & Test

```bash
# Build l'image
docker build -t wan-worker .

# Test en local (nécessite GPU)
docker run --rm -p 8080:8080 --gpus all wan-worker
```

## Specs

- **Modèle**: WAN 2.1 T2V-1.3B (1.3B params)
- **VRAM**: ~8GB minimum
- **Output**: 832x480, 5 secondes
- **GPU**: RTX A4000+ recommandé

## API

**Request:**
```json
{"input": {"prompt": "A cat playing"}}
```

**Response:**
```json
{
  "video_url": "https://storage.runpod.io/wan-videos/wan_abc123.mp4",
  "prompt": "A cat playing"
}
```