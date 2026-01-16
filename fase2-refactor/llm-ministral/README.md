# Ollama + Ministral Setup

Ollama draait buiten de Docker Compose stack om GPU resource conflicts te vermijden.

## Installatie

### Docker container starten

```bash
# Eerste keer
docker run -d --gpus device=0 \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama-nerdcarx \
  -e OLLAMA_KV_CACHE_TYPE=q8_0 \
  -e OLLAMA_KEEP_ALIVE=-1 \
  ollama/ollama

# Daarna starten
docker start ollama-nerdcarx
```

### Model downloaden

```bash
# In de container
docker exec -it ollama-nerdcarx ollama pull ministral-3:14b

# Of specifieke versie
docker exec -it ollama-nerdcarx ollama pull ministral-3:14b-instruct-2512-q8_0
```

## Beschikbare Modellen

| Model | Grootte | Notities |
|-------|---------|----------|
| `ministral-3:14b` | ~15GB | Aanbevolen, q4_k_m quantized |
| `ministral-3:14b-instruct-2512-q8_0` | ~15GB | Hogere kwaliteit |
| `ministral-3:8b` | ~8GB | Lichter, minder VRAM |

## Configuratie

In `config.yml`:

```yaml
ollama:
  url: "http://localhost:11434"  # Of host.docker.internal vanuit container
  model: "ministral-3:14b"
  temperature: 0.15              # NIET hoger - hallucinaties
  top_p: 1.0                     # NIET verlagen
  repeat_penalty: 1.0
  num_ctx: 65536                 # 64k context
```

## VRAM Gebruik

- Model: ~12-15GB VRAM (afhankelijk van quantization)
- Context: ~2-4GB extra bij grote context window

Bij VRAM tekort:
1. Verlaag `num_ctx` naar 32768 of 16384
2. Gebruik 8B model ipv 14B

## Health Check

```bash
# Status
curl http://localhost:11434/api/tags

# Test chat
curl http://localhost:11434/api/chat -d '{
  "model": "ministral-3:14b",
  "messages": [{"role": "user", "content": "Hallo"}],
  "stream": false
}'
```

## Troubleshooting

### Model laadt niet
```bash
# Check logs
docker logs ollama-nerdcarx

# Check GPU
nvidia-smi
```

### Langzame responses
- Check of `OLLAMA_KEEP_ALIVE=-1` is gezet (houdt model in VRAM)
- Check VRAM gebruik: `nvidia-smi`

### OOM errors
- Verlaag `num_ctx` in config.yml
- Gebruik kleiner model
