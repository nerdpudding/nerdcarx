# Ollama + Ministral

> **Note:** Ollama draait als onderdeel van de Docker Compose stack. Start alles met `docker compose up -d` vanuit `fase2-refactor/`.

## Model

| Aspect | Waarde |
|--------|--------|
| Model | `ministral-3:14b-instruct-2512-q8_0` |
| Container | `nerdcarx-ollama` |
| Poort | 11434 |
| GPU | GPU0 (RTX 4090) |
| VRAM | ~15-20GB |

## Configuratie

In `config.yml`:

```yaml
ollama:
  url: "http://ollama:11434"      # Binnen Docker network
  model: "ministral-3:14b"
  temperature: 0.15               # NIET hoger - hallucinaties
  top_p: 1.0                      # NIET verlagen
  repeat_penalty: 1.0
  num_ctx: 65536                  # 64k context
```

**Belangrijk:** Deze parameters zijn officieel van Mistral. Hogere temperature leidt tot hallucinaties.

## Model downloaden (eerste keer)

Na `docker compose up -d`:

```bash
# Model pullen (eenmalig, ~15GB)
docker exec -it nerdcarx-ollama ollama pull ministral-3:14b

# Of specifieke quantization
docker exec -it nerdcarx-ollama ollama pull ministral-3:14b-instruct-2512-q8_0
```

## Beschikbare Modellen

| Model | Grootte | Notities |
|-------|---------|----------|
| `ministral-3:14b` | ~15GB | Standaard, q4_k_m quantized |
| `ministral-3:14b-instruct-2512-q8_0` | ~15GB | Hogere kwaliteit (aanbevolen) |
| `ministral-3:8b` | ~8GB | Lichter, minder VRAM |

## Health Check

```bash
# Vanuit host
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
docker compose logs ollama
nvidia-smi
```

### Langzame eerste response (cold start)
De orchestrator warmt Ollama automatisch op bij startup. Als dit niet werkt:
```bash
# Handmatig warm maken
curl http://localhost:11434/api/chat -d '{
  "model": "ministral-3:14b",
  "messages": [{"role": "user", "content": "test"}],
  "stream": false
}'
```

### OOM errors
- Verlaag `num_ctx` in config.yml (bijv. 32768 of 16384)
- Gebruik kleiner model (`ministral-3:8b`)

### Container herstartte / model uit VRAM
De compose heeft `OLLAMA_KEEP_ALIVE=-1` ingesteld, dus het model blijft in VRAM. Bij herstart laadt het model automatisch opnieuw bij eerste request.
