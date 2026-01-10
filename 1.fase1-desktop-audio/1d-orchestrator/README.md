# Orchestrator - NerdCarX

Simpele FastAPI service die STT output doorstuurt naar de LLM.

> **Quick & Dirty Setup (Tijdelijk)**
>
> Voor nu draait de orchestrator lokaal in de `nerdcarx-vad` conda environment.
> Dit is bewust simpel gehouden voor snelle iteratie tijdens development.
>
> **Later:** Orchestrator wordt een Docker container samen met de rest van de stack.
> Dit gebeurt in fase 1f (Integratie) of wanneer we naar productie-achtige setup gaan.

## Quick Start

```bash
# 1. Zorg dat Ollama draait
docker run -d \
  --gpus device=0 \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama-nerdcarx \
  -e OLLAMA_KV_CACHE_TYPE=q8_0 \
  -e OLLAMA_NUM_PARALLEL=1 \
  ollama/ollama

# 2. Pull het model (eenmalig)
docker exec ollama-nerdcarx ollama pull mistral:ministral-8b-instruct-2412-q8_0

# 3. Activeer conda env en installeer dependencies
conda activate nerdcarx-vad
pip install -r requirements.txt

# 4. Start orchestrator
cd 1.fase1-desktop-audio/1d-orchestrator
uvicorn main:app --host 0.0.0.0 --port 8200 --reload
```

## Endpoints

### Health & Status

```bash
# Health check
curl http://localhost:8200/health

# Status van alle services
curl http://localhost:8200/status
```

### Chat (zonder history)

```bash
curl -X POST http://localhost:8200/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Wat is de hoofdstad van Frankrijk?"}'
```

### Conversation (met history)

```bash
# Start conversatie
curl -X POST http://localhost:8200/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "Hoi, ik ben Ralph", "conversation_id": "ralph-1"}'

# Vervolg (onthoudt context)
curl -X POST http://localhost:8200/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "Wat is mijn naam?", "conversation_id": "ralph-1"}'

# Wis conversatie
curl -X DELETE http://localhost:8200/conversation/ralph-1
```

### Opties

| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `message` | (verplicht) | De vraag/tekst |
| `system_prompt` | NerdCarX prompt | Custom system prompt |
| `temperature` | 0.7 | Creativiteit (0.0-1.0) |
| `num_ctx` | 65536 | Context window (64k) |
| `conversation_id` | "default" | ID voor history tracking |

## Architectuur

```
[VAD] → [Voxtral STT] → tekst
                          ↓
                    [Orchestrator :8200]
                          ↓
                    [Ollama :11434]
                          ↓
                      response
                          ↓
              ┌───────────┴───────────┐
              ↓                       ↓
         [TTS] (later)        [Function Calls] (later)
```

## Configuratie

Huidige defaults in `main.py`:

```python
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:ministral-8b-instruct-2412-q8_0"
VOXTRAL_URL = "http://localhost:8150"
DEFAULT_NUM_CTX = 65536  # 64k
DEFAULT_TEMPERATURE = 0.7
```

## Volgende Stappen

- [ ] VAD script aanpassen om orchestrator te gebruiken i.p.v. direct Voxtral
- [ ] TTS integratie toevoegen
- [ ] Function calling afhandeling
- [ ] WebSocket support voor streaming (optioneel)
