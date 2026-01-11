# Fase 1: Desktop Compleet

**Status:** Actief - basis flow werkt, TTS nog te doen
**Doel:** Volledig werkende desktop demo met spraak-naar-spraak loop

## Huidige Stand (2026-01-11)

```
[Desktop Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral LLM] → response
                                              ↓
                                    + Vision (take_photo tool)
                                    + Emoties (show_emotion tool)
                                    + Centrale config (config.yml)
```

**Wat werkt:** ✅ Alle tests geslaagd
- STT via Voxtral (Docker op GPU1)
- LLM via Ministral 14B Q8 (Ollama op GPU0) - ~20GB VRAM, past met speling
- Orchestrator met centrale config + hot reload
- VAD hands-free gesprekken
- Vision via `take_photo` function call
- Emoties via `show_emotion` function call

**Performance notities:**
- Vision latency ~5-10s (dubbele LLM call: tool detection + image analyse)
- Q8 quantization duidelijk beter dan Q4 voor response kwaliteit
- Cold start na container restart kan eerste request vertragen

**Wat nog moet:**
- TTS integratie (volgende stap)

---

## Structuur

```
fase1-desktop/
├── PLAN.md                 # Dit bestand
├── config.yml              # Centrale configuratie
├── stt-voxtral/            # Speech-to-Text
│   ├── docker/             # Docker setup
│   └── README.md
├── llm-ministral/          # LLM setup (TODO: README)
├── tts/                    # Text-to-Speech (TODO)
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
| LLM | [llm-ministral/](./llm-ministral/) | ✅ Werkt | Ministral 14B Q8 via Ollama |
| TTS | [tts/](./tts/) | 🔜 Volgende | Onderzoek opties |
| Orchestrator | [orchestrator/](./orchestrator/) | ✅ Werkt | FastAPI + config.yml |
| VAD | [vad-desktop/](./vad-desktop/) | ✅ Werkt | Hands-free gesprekken |

---

## Configuratie

Alle settings staan in `config.yml`:

```yaml
ollama:
  model: "ministral-3:14b-instruct-2512-q8_0"
  temperature: 0.15    # Officieel
  top_p: 1.0           # Officieel
  repeat_penalty: 1.0  # Officieel

voxtral:
  temperature: 0.0     # Greedy voor transcriptie

system_prompt: |
  Je bent de AI van NerdCarX...
  GEEN emoji's, GEEN grappen...

vision:
  mock_image_path: "vad-desktop/test_foto.jpg"
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
ollama pull ministral-3:14b-instruct-2512-q8_0

# Terminal 3: Orchestrator
cd fase1-desktop/orchestrator
pip install pyyaml  # indien nodig
uvicorn main:app --port 8200 --reload

# Terminal 4: VAD Conversation
cd fase1-desktop/vad-desktop
python vad_conversation.py
```

**Test endpoints:**
```bash
curl http://localhost:8200/health
curl http://localhost:8200/config
curl http://localhost:8200/tools
```

---

## Volgende Stappen

### 1. TTS Integratie

**Opties te onderzoeken:**
| Optie | Voordelen | Nadelen |
|-------|-----------|---------|
| Piper | Snel, offline, meerdere talen | Minder expressief |
| Coqui XTTS | Nederlands, expressief | Meer VRAM |
| Bark | Zeer expressief | Traag, veel VRAM |
| Kokoro | Snel, goede kwaliteit | Nieuwe optie |

**Criteria:**
- Nederlands ondersteund
- Lage latency (<500ms)
- GPU0 of GPU1 (afhankelijk van VRAM)

### 2. Na TTS

Na TTS integratie is Fase 1 afgerond. Dan:
- → Fase 2: Refactor + Dockerizen

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
| 2026-01-11 | Q8 model bevestigd: 20GB VRAM, goede kwaliteit |

---

[← Terug naar README](../README.md)
