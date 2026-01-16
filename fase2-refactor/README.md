# NerdCarX Fase 2

Gedockerizeerde orchestrator met WebSocket support voor Pi communicatie.

## Architectuur

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │
│  │   Voxtral     │  │  Fish Audio   │  │   Orchestrator    │   │
│  │   (STT)       │  │    (TTS)      │  │    (FastAPI)      │   │
│  │  :8150        │  │   :8250       │  │     :8200         │   │
│  │  GPU1         │  │   GPU0        │  │                   │   │
│  └───────────────┘  └───────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP
                              ▼
                    ┌─────────────────┐
                    │     Ollama      │
                    │   (Ministral)   │
                    │    :11434       │
                    │     GPU0        │
                    └─────────────────┘
                   (draait extern)
```

## Quick Start

### 1. Ollama starten (als niet al draait)

```bash
docker start ollama-nerdcarx

# Of eerste keer:
docker run -d --gpus device=0 \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama-nerdcarx \
  -e OLLAMA_KV_CACHE_TYPE=q8_0 \
  -e OLLAMA_KEEP_ALIVE=-1 \
  ollama/ollama
```

### 2. Stack starten

```bash
cd fase2-refactor
docker compose up -d
```

Eerste keer duurt even:
- Voxtral: ~12GB model download
- Fish Audio: checkpoints download
- Orchestrator: image build

### 3. Status checken

```bash
# Health check
curl http://localhost:8200/health

# Alle services status
curl http://localhost:8200/status

# Configuratie
curl http://localhost:8200/config
```

### 4. Testen

```bash
# Chat (stateless)
curl -X POST http://localhost:8200/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hallo, hoe heet je?"}'

# Conversation (met history en TTS)
curl -X POST http://localhost:8200/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "Wat kun je allemaal?"}'

# WebSocket test (met wscat)
wscat -c "ws://localhost:8200/ws?conversation_id=test"
```

## Folder Structuur

```
fase2-refactor/
├── docker-compose.yml          # Voxtral + TTS + Orchestrator
├── config.yml                  # Centrale configuratie
├── .env.example
├── README.md
│
├── orchestrator/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry
│       ├── config.py           # Config loading
│       ├── routes/             # API endpoints
│       ├── services/           # Provider abstracties
│       ├── models/             # Data models
│       ├── websocket/          # WebSocket support
│       └── utils/              # Helpers
│
├── stt-voxtral/                # Voxtral Docker setup
├── llm-ministral/              # Ollama instructies
└── tts/fishaudio/references/   # Voice references
```

## API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /status` - Status van alle services
- `GET /config` - Huidige configuratie
- `GET /tools` - Beschikbare tools
- `POST /reload-config` - Hot reload config

### Chat
- `POST /chat` - Stateless chat
- `POST /conversation` - Chat met history + TTS
- `POST /conversation/streaming` - Streaming TTS (SSE)
- `DELETE /conversation/{id}` - Wis conversation
- `GET /conversations` - Lijst conversations

### WebSocket
- `WS /ws` - Pi communicatie endpoint
- `GET /ws/clients` - Actieve WebSocket clients

## WebSocket Protocol

### Pi → Desktop

```json
// Audio processing
{
  "type": "audio_process",
  "conversation_id": "default",
  "payload": {
    "audio_base64": "...",
    "language": "nl"
  }
}

// Heartbeat
{
  "type": "heartbeat",
  "conversation_id": "default"
}
```

### Desktop → Pi

```json
// Response
{
  "type": "response",
  "conversation_id": "default",
  "payload": {
    "text": "...",
    "emotion": "happy"
  }
}

// Audio chunk
{
  "type": "audio_chunk",
  "payload": {
    "audio_base64": "...",
    "sentence": "...",
    "is_last": false
  }
}

// Function call
{
  "type": "function_call",
  "payload": {
    "name": "show_emotion",
    "arguments": {"emotion": "excited"}
  }
}
```

## Development

### Lokaal draaien (zonder Docker)

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

### Logs bekijken

```bash
# Alle services
docker compose logs -f

# Specifieke service
docker compose logs -f orchestrator
docker compose logs -f voxtral
docker compose logs -f tts
```

### Rebuilden

```bash
# Orchestrator rebuilden
docker compose up -d --build orchestrator

# Alles rebuilden
docker compose up -d --build
```

## Configuratie

Zie `config.yml` voor alle opties. Belangrijke settings:

```yaml
ollama:
  model: "ministral-3:14b"
  temperature: 0.15

tts:
  streaming: true     # TTS per zin
  temperature: 0.5    # Expressiviteit

websocket:
  enabled: true
  heartbeat_interval: 30
```

## Troubleshooting

### Voxtral start niet
- Check GPU1 beschikbaarheid: `nvidia-smi`
- Logs: `docker compose logs voxtral`
- Model download kan lang duren (~12GB)

### TTS geen geluid
- Check Fish Audio health: `curl localhost:8250/v1/health`
- Reference audio bestaat: `ls tts/fishaudio/references/`

### WebSocket verbinding faalt
- Check of websocket.enabled=true in config
- Port 8200 open in firewall

### Ollama timeout
- Check of Ollama draait: `curl localhost:11434/api/tags`
- Model geladen: `ollama list`
