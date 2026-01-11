# Orchestrator - NerdCarX

FastAPI service die STT, LLM, Vision en Function Calling aan elkaar koppelt.

> **Quick & Dirty Setup (Tijdelijk)**
>
> Draait lokaal in `nerdcarx-vad` conda environment.
> Docker komt later wanneer de base stabiel is.

## Huidige Features

- **Chat/Conversation** - met history management
- **Vision** - via `take_photo` tool (on-demand)
- **Function Calling** - `show_emotion` en `take_photo` tools
- **Tool loop** - automatisch tool results verwerken
- **Centrale config** - `config.yml` met hot reload

## Quick Start

```bash
# 1. Zorg dat Ollama draait
docker run -d --gpus device=0 -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama-nerdcarx \
  -e OLLAMA_KV_CACHE_TYPE=q8_0 \
  -e OLLAMA_KEEP_ALIVE=-1 \
  ollama/ollama
docker exec ollama-nerdcarx ollama pull ministral-3:14b-instruct-2512-q8_0

# 2. Start orchestrator
conda activate nerdcarx-vad
cd fase1-desktop/orchestrator
uvicorn main:app --host 0.0.0.0 --port 8200 --reload
```

## Endpoints

### Health & Config

```bash
curl http://localhost:8200/health   # Service status
curl http://localhost:8200/config   # Huidige configuratie
curl http://localhost:8200/tools    # Beschikbare tools
curl -X POST http://localhost:8200/reload-config  # Config herladen
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
                    [Ollama :11434] (Ministral 14B Q8)
                          ↓
                    tool_calls? → execute (show_emotion, take_photo)
                          ↓
                    response + function_calls
```

## Configuratie

Alle configuratie staat in `../config.yml`:

```yaml
ollama:
  url: "http://localhost:11434"
  model: "ministral-3:14b-instruct-2512-q8_0"
  temperature: 0.15
  top_p: 1.0
  repeat_penalty: 1.0
  num_ctx: 65536

voxtral:
  url: "http://localhost:8150"
```

Hot reload: `curl -X POST http://localhost:8200/reload-config`

## Function Calling

De orchestrator handelt de volledige tool calling loop af:

1. Request naar Ollama met tools
2. Als tool_calls in response: execute en stuur result terug
3. Herhaal tot finale tekst response

Huidige tools:
- `show_emotion` - toon emotie op OLED (happy, sad, angry, etc.)
- `take_photo` - maak foto en analyseer (vision on-demand)

## Bekende Issues

- Ministral heeft sterke "Le Chat" persoonlijkheid
- Output soms te speels ondanks system prompt
- Prompt tuning ongoing

## Volgende Stappen

- [ ] TTS integratie
- [ ] Dockerizen
- [ ] Betere prompt engineering
