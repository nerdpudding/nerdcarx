# Fase 2: Refactor + Docker + Pi Communicatie

**Status:** WERKEND (2026-01-16) - Stack draait, STT/LLM/TTS pipeline getest
**Vorige fase:** Fase 1 Desktop - AFGEROND

---

## Doel

Een **eigen folder structuur** opzetten met:
- Gedockerizeerde orchestrator (weg van gedeelde conda)
- WebSocket communicatie voor Pi ↔ Desktop
- Modulaire, toekomstbestendige code (SOLID/KISS/DRY)
- Abstractielaag voor swappable providers (LLM, STT, TTS)
- Voorbereiding op camera streaming (Fase 3+)

---

## Folder Structuur

```
fase2-refactor/
├── docker-compose.yml          # Voxtral + TTS + Orchestrator
├── config.yml                  # Centrale config
├── .env.example
├── README.md
│
├── orchestrator/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry (slim)
│       ├── config.py           # Config loading + DI
│       ├── routes/             # API endpoints
│       │   ├── chat.py         # /chat, /conversation
│       │   ├── health.py       # /health, /status
│       │   └── websocket.py    # /ws voor Pi
│       ├── services/           # Provider abstracties
│       │   ├── stt/            # STT providers (voxtral, etc)
│       │   ├── llm/            # LLM providers (ollama, etc)
│       │   ├── tts/            # TTS providers (fishaudio, etc)
│       │   └── tools/          # Function calling (emotion, vision)
│       ├── models/             # Pydantic schemas
│       │   ├── schemas.py
│       │   ├── emotion.py
│       │   └── conversation.py
│       ├── websocket/          # Pi communicatie
│       │   ├── protocol.py
│       │   ├── manager.py
│       │   └── handlers.py
│       └── utils/
│           └── text_normalization.py
│
├── stt-voxtral/                # Kopie van fase1 (al Docker)
│   └── docker/
│
├── llm-ministral/
│   └── README.md               # Ollama setup instructies
│
└── tts/
    └── fishaudio/
        ├── checkpoints/        # Model checkpoints (openaudio-s1-mini)
        └── references/         # Reference audio (dutch2/)
```

**NIET gekopieerd:** `vad-desktop/` → wordt Pi-based met wake word (Fase 3)

---

## Docker Architectuur

### Volledige Stack (docker-compose.yml)

| Service | Port | GPU | Container | Notes |
|---------|------|-----|-----------|-------|
| ollama | 11434 | GPU0 (4090) | nerdcarx-ollama | Shared volume met andere ollama |
| voxtral | 8150 | GPU1 (5070 Ti) | nerdcarx-voxtral | STT via vLLM |
| tts | 8250 | GPU0 (4090) | nerdcarx-tts | Fish Audio S1-mini |
| orchestrator | 8200 | CPU | nerdcarx-orchestrator | FastAPI |

**Volumes:**
- `ollama` (external) - Gedeeld met andere ollama container
- `tts-cache` - Compile cache voor snellere TTS restarts
- `./tts/fishaudio/checkpoints` - Model checkpoints (lokaal)
- `./tts/fishaudio/references` - Reference audio (lokaal)

**Note:** Ollama zit nu IN de stack. Bij `docker compose up -d` start alles samen.

---

## Service Abstractie (SOLID)

### Protocol Pattern

Elke service (STT, LLM, TTS) krijgt een `Protocol` interface:

```python
class STTProvider(Protocol):
    async def transcribe(self, audio: bytes, language: str = "nl") -> str: ...
    async def health_check(self) -> bool: ...

class LLMProvider(Protocol):
    async def chat(self, messages: list, tools: list = None) -> tuple[str, list]: ...
    async def health_check(self) -> bool: ...

class TTSProvider(Protocol):
    async def synthesize(self, text: str, emotion: str = "neutral") -> bytes: ...
    async def health_check(self) -> bool: ...
```

**Waarom Protocol?**
- Lichter dan ABC's
- Duck typing - geen inheritance nodig
- Makkelijk te mocken
- Toekomst: alternatieve providers direct toe te voegen

---

## WebSocket Protocol (Pi ↔ Desktop)

### Message Types

**Pi → Desktop:**
- `AUDIO_PROCESS` - Audio + sensor context voor processing
- `WAKE_WORD` - Wake word gedetecteerd
- `SENSOR_UPDATE` - Sensor data (ToF, ultrasonic)
- `HEARTBEAT` - Keep-alive (30s interval)

**Desktop → Pi:**
- `RESPONSE` - LLM response text
- `AUDIO_CHUNK` - TTS audio per zin (streaming)
- `FUNCTION_CALL` - Robot actie (show_emotion, etc)
- `ERROR` - Foutmelding

### Flow

```
Pi                                Desktop
│                                     │
├─── WebSocket Connect ──────────────►│
├─── WAKE_WORD ──────────────────────►│
├─── AUDIO_PROCESS (wav base64) ─────►│
│                                     │
│     [STT → LLM → TTS per zin]       │
│                                     │
│◄──────────────── RESPONSE (text) ───┤
│◄──────────────── AUDIO_CHUNK ───────┤ (herhaald)
│◄──────────────── FUNCTION_CALL ─────┤
│                                     │
├─── HEARTBEAT ──────────────────────►│ (elke 30s)
```

---

## Implementatie Checklist

### Stap 1: Folder Setup
- [x] `fase2-refactor/` folder structuur aanmaken
- [x] config.yml kopiëren van fase1 + URLs aanpassen
- [x] stt-voxtral/ kopiëren van fase1
- [x] tts/fishaudio/references/ kopiëren

### Stap 2: Orchestrator Basis
- [x] `app/config.py` - config loading met DI
- [x] `app/models/schemas.py` - Pydantic request/response models
- [x] `app/models/emotion.py` - emotion state machine
- [x] `app/utils/text_normalization.py` - TTS preprocessing

### Stap 3: Service Abstracties
- [x] `services/stt/base.py` + `voxtral.py`
- [x] `services/llm/base.py` + `ollama.py`
- [x] `services/tts/base.py` + `fishaudio.py`
- [x] `services/tools/` - emotion, vision tools

### Stap 4: Routes
- [x] `routes/health.py` - /health, /status, /config
- [x] `routes/chat.py` - /chat, /conversation, /conversation/streaming, /audio-conversation
- [x] `app/main.py` - FastAPI wiring

**Nieuwe endpoint:** `/audio-conversation` - Volledige audio pipeline (Audio in → STT → LLM → TTS → Audio uit)

### Stap 5: WebSocket
- [x] `websocket/protocol.py` - message types
- [x] `websocket/manager.py` - connection manager
- [x] `websocket/handlers.py` - message handlers
- [x] `routes/websocket.py` - /ws endpoint

### Stap 6: Docker
- [x] `orchestrator/Dockerfile`
- [x] `orchestrator/requirements.txt` (incl. python-multipart)
- [x] `docker-compose.yml` (incl. Ollama, tts-cache volume)
- [x] Health checks werken (alle services healthy)
- [x] `docker compose up -d` start hele stack

### Stap 7: Documentatie
- [x] `README.md` - setup guide
- [x] `llm-ministral/README.md` - Ollama instructies

---

## Config Management

```yaml
# config.yml met environment variable fallbacks
ollama:
  url: "${OLLAMA_URL:-http://localhost:11434}"

voxtral:
  url: "${VOXTRAL_URL:-http://localhost:8150}"

tts:
  url: "${TTS_URL:-http://localhost:8250}"
  streaming: true

websocket:
  enabled: true
  heartbeat_interval: 30
  audio_chunk_threshold: 3  # zinnen voor URL-streaming

# Toekomst: provider switching
# stt_provider: "voxtral"    # of "whisper", "deepgram"
# llm_provider: "ollama"     # of "openai", "anthropic"
# tts_provider: "fishaudio"  # of "elevenlabs"
```

---

## Verificatie

```bash
# 1. Start stack (Ollama zit er nu in)
cd fase2-refactor
docker compose up -d

# 2. Check status
docker ps --filter "name=nerdcarx" --format "table {{.Names}}\t{{.Status}}"

# 3. Health checks
curl http://localhost:8200/health
curl http://localhost:8200/status

# 4. Chat test (text only)
curl -X POST http://localhost:8200/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hallo, hoe heet je?"}'

# 5. Audio pipeline test (STT → LLM → TTS)
curl -X POST http://localhost:8200/audio-conversation \
  -F "audio=@test.wav" \
  --output response.wav
aplay response.wav

# 6. WebSocket test (wscat)
wscat -c ws://localhost:8200/ws
```

---

## Exit Criteria

Fase 2 is klaar wanneer:
- [x] `docker compose up -d` start hele stack (ollama + voxtral + tts + orchestrator)
- [x] Health checks werken voor alle services (alle 4 healthy)
- [x] Chat endpoint werkt (/chat - text → response)
- [x] Audio pipeline werkt (/audio-conversation - audio → STT → LLM → TTS → audio)
- [x] WebSocket endpoint werkt (verbinding, heartbeat, error handling, audio_process)
- [x] Code is modulair (services, routes, models gescheiden)
- [x] Documentatie compleet (README met quick start)

**✅ FASE 2 AFGEROND (2026-01-16)**

---

## Volgende Fase

**Fase 3: Pi Integratie**
- Wake word op Pi (Porcupine)
- VAD + audio capture op Pi
- WebSocket client op Pi
- OLED emotion display
- Camera streaming voorbereiden

---

[← Terug naar README](../README.md)
