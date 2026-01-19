# NerdCarX Orchestrator

De centrale hub die alle AI services verbindt: STT, LLM, TTS, en de Pi robot.

## Architectuur

```
                          ┌─────────────────────────────────────────┐
                          │           Orchestrator (8200)           │
                          ├─────────────────────────────────────────┤
    Pi ◄───WebSocket────► │  routes/                                │
                          │    ├── health.py    /health, /status    │
                          │    ├── chat.py      /chat, /conversation│
                          │    └── websocket.py /ws                 │
                          │                                         │
                          │  services/ (Protocol-based)             │
                          │    ├── stt/      VoxtralSTT             │
                          │    ├── llm/      OllamaLLM              │
                          │    ├── tts/      FishAudioTTS           │
                          │    └── tools/    Emotion, Vision, Sleep │
                          │                                         │
                          │  models/                                │
                          │    ├── emotion.py       State machine   │
                          │    ├── conversation.py  History mgmt    │
                          │    └── schemas.py       Pydantic models │
                          └───────────┬─────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
        ┌──────────┐           ┌──────────┐            ┌──────────┐
        │  Voxtral │           │  Ollama  │            │   TTS    │
        │  (8150)  │           │ (11434)  │            │  (8250)  │
        └──────────┘           └──────────┘            └──────────┘
```

## Design Keuzes

### Protocol Pattern (niet ABC)

Services gebruiken Python's `Protocol` in plaats van abstracte base classes:

```python
@runtime_checkable
class HealthCheckable(Protocol):
    async def health_check(self) -> bool: ...
```

**Waarom:**
- Lichter dan ABC inheritance
- Duck typing - geen `class Foo(AbstractFoo)` nodig
- Makkelijker te mocken voor tests
- Pythonic

### Emotion State Machine

De robot simuleert emoties die beïnvloed worden door de gebruiker:

- **15 emoties**: happy, sad, angry, surprised, neutral, curious, confused, excited, thinking, shy, love, tired, bored, proud, worried
- **Persistent**: Emotie blijft behouden tussen berichten
- **Auto-reset**: Na 5 min inactiviteit → neutral
- **LLM-driven**: Het LLM beslist wanneer `show_emotion()` wordt aangeroepen

### Tool Registry

Tools worden geregistreerd en kunnen lokaal of remote draaien:

| Tool | Remote? | Beschrijving |
|------|---------|--------------|
| `show_emotion` | Ja | OLED display op Pi |
| `take_photo` | Ja | Camera op Pi |
| `go_to_sleep` | Ja | Sleep mode trigger |

Remote tools worden via WebSocket naar de Pi gestuurd. Zie [D016](../../DECISIONS.md) voor het Remote Tool Pattern.

## Folder Structuur

```
orchestrator/
├── Dockerfile              # Multi-stage build
├── requirements.txt        # Python dependencies
└── app/
    ├── main.py             # FastAPI entry (slim)
    ├── config.py           # Config loading + env var expansion
    │
    ├── routes/
    │   ├── health.py       # /health, /status, /config, /tools
    │   ├── chat.py         # /chat, /conversation, streaming
    │   └── websocket.py    # /ws endpoint voor Pi
    │
    ├── services/
    │   ├── base.py         # Protocol definitions
    │   ├── stt/            # VoxtralSTT
    │   ├── llm/            # OllamaLLM
    │   ├── tts/            # FishAudioTTS
    │   └── tools/          # EmotionTool, VisionTool, SleepTool
    │
    ├── models/
    │   ├── schemas.py      # Request/Response Pydantic models
    │   ├── emotion.py      # EmotionManager state machine
    │   └── conversation.py # ConversationManager history
    │
    ├── websocket/
    │   ├── protocol.py     # Message types (Pi ↔ Desktop)
    │   ├── manager.py      # ConnectionManager
    │   └── handlers.py     # MessageHandler + remote tools
    │
    └── utils/
        ├── text_normalization.py  # "API" → "aa-pee-ie"
        └── debug_logger.py        # Timing per stap
```

## API Endpoints

### Health & Status

| Endpoint | Beschrijving |
|----------|--------------|
| `GET /health` | Health check |
| `GET /status` | Status van alle services |
| `GET /config` | Huidige configuratie |
| `GET /tools` | Beschikbare tools |
| `POST /reload-config` | Hot reload config |

### Chat

| Endpoint | Beschrijving |
|----------|--------------|
| `POST /chat` | Stateless chat (geen history) |
| `POST /conversation` | Chat met history + TTS |
| `POST /conversation/streaming` | Streaming TTS per zin (SSE) |
| `DELETE /conversation/{id}` | Wis conversation history |
| `GET /conversations` | Lijst actieve conversations |

### WebSocket

| Endpoint | Beschrijving |
|----------|--------------|
| `WS /ws` | Pi ↔ Desktop communicatie |
| `GET /ws/clients` | Actieve WebSocket clients |

## WebSocket Protocol

### Pi → Orchestrator

```json
{
  "type": "audio_process",
  "conversation_id": "default",
  "timestamp": 1234567890.123,
  "payload": {
    "audio_base64": "...",
    "sample_rate": 16000
  }
}
```

Types: `audio_process`, `wake_word`, `heartbeat`, `sensor_update`, `function_result`

### Orchestrator → Pi

```json
{
  "type": "response",
  "conversation_id": "default",
  "payload": {
    "text": "Hallo!",
    "emotion": "happy"
  }
}
```

Types: `response`, `audio_chunk`, `function_call`, `function_request`, `error`

## Lokaal Ontwikkelen

### Zonder Docker

```bash
cd orchestrator

# Virtual environment
python -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Start (met auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8200 --reload
```

### Environment Variables

De orchestrator ondersteunt env var expansion in config.yml:

```yaml
ollama:
  url: "${OLLAMA_URL:-http://localhost:11434}"
```

In Docker Compose worden deze automatisch gezet.

## Features

### Ollama Warmup

Bij startup wordt Ollama automatisch "opgewarmd" (model in VRAM geladen). Dit voorkomt cold start delays bij de eerste request.

### Debug Logging

Met `debug.enabled: true` in config.yml krijg je timing per stap:

```
[TURN 5] ════════════════════════════════════════
  STT:   324ms   "Wat zie je?"
  LLM:   1.2s    tool_calls: [take_photo]
  TOOL:  4.8s    take_photo → "Een bureau met laptop"
  TTS:   0.6s    streaming: 2 chunks
  TOTAL: 6.9s
```

### Text Normalisatie

Nederlandse uitspraak wordt verbeterd:
- `API` → `aa-pee-ie`
- `100` → `honderd`
- `ASML` → `aa-es-em-el`

## Configuratie

Zie `../config.yml` voor alle opties. Belangrijke secties:

```yaml
orchestrator:
  host: "0.0.0.0"
  port: 8200

ollama:
  model: "ministral-3:14b"
  temperature: 0.15          # NIET hoger!

tts:
  enabled: true
  streaming: true            # Per-zin TTS

websocket:
  enabled: true
  heartbeat_interval: 30

emotions:
  default: "neutral"
  auto_reset_minutes: 5

debug:
  enabled: true
  verbose: false
```
