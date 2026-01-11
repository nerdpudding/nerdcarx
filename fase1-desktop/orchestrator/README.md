# Orchestrator - NerdCarX

FastAPI service die STT, LLM, Vision en Function Calling aan elkaar koppelt.

> **Quick & Dirty Setup (Tijdelijk)**
>
> Draait lokaal in `nerdcarx-vad` conda environment.
> Docker komt later wanneer de base stabiel is.

## Huidige Features

- **Chat/Conversation** - met history management
- **Vision** - foto meesturen bij elke request
- **Function Calling** - show_emotion tool
- **Tool loop** - automatisch tool results verwerken

## Quick Start

```bash
# 1. Zorg dat Ollama draait
docker run -d --gpus device=0 -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama-nerdcarx -e OLLAMA_KV_CACHE_TYPE=q8_0 ollama/ollama
docker exec ollama-nerdcarx ollama pull ministral-3:14b

# 2. Start orchestrator
conda activate nerdcarx-vad
cd 1.fase1-desktop-audio/1d-orchestrator
uvicorn main:app --host 0.0.0.0 --port 8200 --reload
```

## Endpoints

### Health & Status

```bash
curl http://localhost:8200/health
curl http://localhost:8200/status
```

### Chat (zonder history)

```bash
curl -X POST http://localhost:8200/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hallo"}'
```

### Conversation (met history + vision)

```bash
# Met image (base64)
curl -X POST http://localhost:8200/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Wat zie je?",
    "conversation_id": "test-1",
    "image_base64": "<base64 encoded image>"
  }'
```

### Parameters

| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `message` | (verplicht) | User input tekst |
| `image_base64` | null | Base64 encoded image (robot camera view) |
| `system_prompt` | NerdCarX prompt | Custom system prompt |
| `temperature` | 0.15 | Creativiteit (Ministral default) |
| `num_ctx` | 65536 | Context window (64k) |
| `conversation_id` | "default" | ID voor history tracking |
| `enable_tools` | true | Function calling aan/uit |

## Architectuur

```
[VAD] → [Voxtral STT] → tekst
                          ↓
                    [Orchestrator :8200]
                          ↓
                    inject image_base64
                          ↓
                    [Ollama :11434] (Ministral 14B)
                          ↓
                    tool_calls? → execute → get final response
                          ↓
                    response + function_calls
```

## Configuratie

In `main.py`:

```python
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "ministral-3:14b"
VOXTRAL_URL = "http://localhost:8150"
DEFAULT_NUM_CTX = 65536
DEFAULT_TEMPERATURE = 0.15  # Ministral default
```

## Function Calling

De orchestrator handelt de volledige tool calling loop af:

1. Request naar Ollama met tools
2. Als tool_calls in response: execute en stuur result terug
3. Herhaal tot finale tekst response

Huidige tool: `show_emotion` (happy, sad, angry, etc.)

## Bekende Issues

- Ministral heeft sterke "Le Chat" persoonlijkheid
- Output soms te speels ondanks system prompt
- Prompt tuning ongoing

## Volgende Stappen

- [ ] TTS integratie
- [ ] Dockerizen
- [ ] Betere prompt engineering
