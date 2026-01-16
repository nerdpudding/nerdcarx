# Fase 1: Desktop Pipeline - AFGEROND ✅

**Status:** ✅ AFGEROND - Klaar voor Fase 2
**Doel:** Volledig werkende desktop demo met spraak-naar-spraak loop
**Datum:** 2026-01-16

## Architectuur

```
[Desktop Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral LLM] → [TTS] → Speaker
                                              ↓
                                    + Vision (take_photo tool)
                                    + Emoties (show_emotion tool)
                                    + Text normalisatie (NL uitspraak)
                                    + Pseudo-streaming (per zin)
                                    + Spatiebalk interrupt
```

## Geïmplementeerde Features

**Core Pipeline:** ✅ Volledig werkend
- STT via Voxtral Mini 3B (Docker op GPU1)
- LLM via Ministral 14B (Ollama op GPU0)
- TTS via Fish Audio S1-mini (Docker, port 8250)
- Orchestrator met centrale config (config.yml)
- VAD hands-free gesprekken met conversation history

**Function Calling:**
- `take_photo` - Camera foto analyseren
- `show_emotion` - Emotie state wijzigen

**TTS Verbeteringen:**
- Text normalisatie: acroniemen, getallen, haakjes naar NL fonetiek
- 30s ElevenLabs reference audio met alle emoties
- Pseudo-streaming: TTS per zin voor snellere perceived latency
- Spatiebalk interrupt tijdens audio playback

**Performance:**
- STT latency: 150-750ms
- LLM latency: 700-1300ms
- TTS latency: ~600ms per zin (streaming) / ~1.2s (batch)
- Perceived latency: ~1.1s (streaming) vs ~3.6s (batch)

---

## Structuur

```
fase1-desktop/
├── README.md               # Dit bestand
├── TODO.md                 # Openstaande punten
├── config.yml              # Centrale configuratie
├── stt-voxtral/            # Speech-to-Text
│   ├── docker/             # Docker setup
│   └── README.md
├── llm-ministral/          # LLM setup
├── tts/                    # Text-to-Speech (Fish Audio)
│   ├── README.md
│   └── fishaudio/          # Fish Audio setup
│       ├── README.md
│       └── elevenreference/ # NL reference audio
├── orchestrator/           # FastAPI orchestrator
│   └── main.py
└── vad-desktop/            # VAD hands-free testing
    └── vad_conversation.py
```

---

## Onderdelen

| Onderdeel | Folder | Status | Beschrijving |
|-----------|--------|--------|--------------|
| STT | [stt-voxtral/](./stt-voxtral/) | ✅ Werkt | Docker container op GPU1 |
| LLM | [llm-ministral/](./llm-ministral/) | ✅ Werkt | Ministral 8B/14B via Ollama |
| TTS | [tts/](./tts/) | ✅ Werkt | Fish Audio S1-mini (port 8250) |
| Orchestrator | [orchestrator/](./orchestrator/) | ✅ Werkt | FastAPI + config.yml + Fish Audio |
| VAD | [vad-desktop/](./vad-desktop/) | ✅ Werkt | Hands-free gesprekken |

---

## Configuratie

Alle settings staan in `config.yml`:

```yaml
ollama:
  model: "ministral-3:14b"
  temperature: 0.15    # Officieel recommended
  top_p: 1.0           # Officieel recommended
  repeat_penalty: 1.0  # Officieel recommended

voxtral:
  temperature: 0.0     # Greedy decoding voor accuracy

tts:  # Fish Audio S1-mini
  url: "http://localhost:8250"
  enabled: true
  reference_id: "dutch2"      # 30s ElevenLabs NL reference
  temperature: 0.5            # Expressiviteit
  top_p: 0.6                  # Diversiteit
  streaming: true             # Per-zin TTS (snellere perceived latency)

system_prompt: |
  Je bent NerdCarX, een kleine robotauto...

emotions:
  default: "neutral"
  available: [happy, sad, angry, surprised, neutral, curious, ...]
```

---

## Quick Start

```bash
# Terminal 1: Voxtral STT (GPU1)
cd fase1-desktop/stt-voxtral/docker
docker compose up -d

# Terminal 2: Ollama LLM (GPU0)
ollama serve
# In andere terminal:
ollama pull ministral-3:8b  # of ministral-3:14b-instruct-2512-q8_0

# Terminal 3: Fish Audio TTS (Docker)
cd original_fish-speech-REFERENCE
docker run -d --gpus device=0 --name fish-tts \
    -v $(pwd)/checkpoints:/app/checkpoints \
    -v $(pwd)/references:/app/references \
    -p 8250:8080 --entrypoint uv \
    fishaudio/fish-speech \
    run tools/api_server.py --listen 0.0.0.0:8080 --compile
# References zijn persistent - dutch2 is al aanwezig

# Terminal 4: Orchestrator
conda activate nerdcarx-vad
cd fase1-desktop/orchestrator
uvicorn main:app --port 8200 --reload

# Terminal 5: VAD Conversation
cd fase1-desktop/vad-desktop
python vad_conversation.py
```

**Test endpoints:**
```bash
curl http://localhost:8200/health   # Orchestrator
curl http://localhost:8200/status   # Alle services
curl http://localhost:8250/v1/health   # Fish Audio TTS
```

---

## Afgeronde Verbeteringen

### TTS Nederlandse Uitspraak ✅
- System prompt aangepast: korte antwoorden (1-3 zinnen), geen markdown
- Text normalisatie: acroniemen → NL fonetiek ("API" → "aa-pee-ie")
- Getallen → woorden ("247" → "tweehonderdzevenenveertig")
- 30s ElevenLabs reference met alle emoties en probleemwoorden

### Pseudo-Streaming ✅
- LLM genereert volledige response
- Response wordt gesplitst in zinnen
- TTS per zin via SSE stream
- Audio direct afgespeeld terwijl volgende zin TTS draait
- **~3x snellere perceived latency**

### Playback Interrupt ✅
- Spatiebalk onderbreekt audio playback
- Werkt in streaming mode
- Terminal settings correct hersteld bij exit

## Bekende Beperkingen (Acceptabel)

| Issue | Opmerking |
|-------|-----------|
| Sommige woorden Engels | Fish Audio limitatie |
| Vraagintonatie niet altijd goed | Model limitatie |
| Kleine pauzes tussen zinnen | Trade-off voor snelheid |

## Volgende Stap

**→ Fase 2: Pipeline testen op Raspberry Pi 5**

---

## TTS Keuze (D009)

**Gekozen:** Fish Audio S1-mini (vervangt Chatterbox)

| Aspect | Waarde |
|--------|--------|
| Model | fishaudio/openaudio-s1-mini |
| Latency | ~600ms per zin (streaming) |
| Nederlands | Via 30s ElevenLabs reference (dutch2) |
| Parameters | temperature=0.5, top_p=0.6 |

**Geteste alternatieven:**
| Model | Latency | Status |
|-------|---------|--------|
| Chatterbox | 5-20s | ❌ Te traag |
| VibeVoice | 1-2s | ❌ Belgisch accent |
| Coqui XTTS-v2 | - | ❌ Project dood |
| Fish Audio | ~600ms | ✅ GEKOZEN |

**Reference audio:** `original_fish-speech-REFERENCE/references/dutch2/reference.mp3` (30s)

---

## Voortgang

| Datum | Update |
|-------|--------|
| 2026-01-10 | STT (Voxtral) werkt in Docker |
| 2026-01-10 | VAD desktop scripts gemaakt |
| 2026-01-11 | Orchestrator met function calling |
| 2026-01-11 | Vision als take_photo tool |
| 2026-01-11 | Centrale config.yml |
| 2026-01-11 | Repo reorganisatie (D006) |
| 2026-01-11 | Alle tests geslaagd (spraak, vision, emoties) |
| 2026-01-11 | TTS: Chatterbox getest maar te traag (5-20s) |
| 2026-01-11 | TTS: Fish Audio S1-mini gekozen (D009) - ~1.2s |
| 2026-01-11 | Config.yml bijgewerkt voor Fish Audio |
| 2026-01-11 | Orchestrator aangepast voor Fish Audio API |
| 2026-01-16 | Text normalisatie voor NL uitspraak |
| 2026-01-16 | 30s ElevenLabs reference audio |
| 2026-01-16 | Pseudo-streaming: TTS per zin via SSE |
| 2026-01-16 | Spatiebalk interrupt voor audio playback |
| 2026-01-16 | **Fase 1 AFGEROND** |

---

[← Terug naar README](../README.md)
