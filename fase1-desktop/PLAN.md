# Fase 1: Desktop Compleet

**Status:** ✅ Alle onderdelen geïmplementeerd
**Doel:** Volledig werkende desktop demo met spraak-naar-spraak loop

## Huidige Stand (2026-01-11)

```
[Desktop Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral LLM] → [TTS] → audio
                                              ↓
                                    + Vision (take_photo tool)
                                    + Emoties (show_emotion tool)
                                    + Centrale config (config.yml)
```

**Wat werkt:** ✅ Alle tests geslaagd
- STT via Voxtral (Docker op GPU1)
- LLM via Ministral 8B/14B (Ollama op GPU0)
- TTS via Chatterbox Multilingual (conda env: nerdcarx-tts)
- Orchestrator met centrale config + hot reload
- VAD hands-free gesprekken
- Vision via `take_photo` function call
- Emoties via `show_emotion` function call

**Performance notities:**
- Vision latency ~5-10s (dubbele LLM call: tool detection + image analyse)
- TTS latency ~1-2s per zin
- Q8 quantization duidelijk beter dan Q4 voor response kwaliteit
- Cold start na container restart kan eerste request vertragen

**Wat nog moet:**
- ~~End-to-end testing met VAD audio playback~~ ✅ Getest (2026-01-11)

**Bekende issues (zie TESTPLAN.md):**
- TTS latency: 5-20 sec (bottleneck)
- TTS spreeksnelheid: te snel
- VRAM: ~18.3GB, lijkt toe te nemen

---

## Structuur

```
fase1-desktop/
├── PLAN.md                 # Dit bestand
├── config.yml              # Centrale configuratie
├── stt-voxtral/            # Speech-to-Text
│   ├── docker/             # Docker setup
│   └── README.md
├── llm-ministral/          # LLM setup
│   └── README.md
├── tts/                    # Text-to-Speech (Chatterbox)
│   ├── README.md
│   ├── tts_service.py      # FastAPI service (port 8250)
│   └── test_chatterbox.py  # Test script
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
| TTS | [tts/](./tts/) | ✅ Werkt | Chatterbox Multilingual (port 8250) |
| Orchestrator | [orchestrator/](./orchestrator/) | ✅ Werkt | FastAPI + config.yml + TTS integratie |
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
ollama pull ministral-3:8b  # of ministral-3:14b-instruct-2512-q8_0

# Terminal 3: TTS Service (aparte conda env!)
conda activate nerdcarx-tts
cd fase1-desktop/tts
uvicorn tts_service:app --port 8250

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
curl http://localhost:8250/health   # TTS
```

---

## Volgende Stappen

### 1. End-to-end Testing ✅

- [x] VAD audio playback integreren
- [x] Volledige loop testen: spraak → STT → LLM → TTS → audio
- [x] Timing per component toegevoegd

### 2. Fase 1 Afronden

Fase 1 is technisch compleet en getest. Bekende issues:
- TTS latency 5-20 sec (Q006)
- TTS te snel (Q007)
- VRAM memory concern (Q008)

**Optioneel (later):**
- Voice reference voor Chatterbox
- Fine-tune emotie → exaggeration mapping
- TTS latency optimalisatie

**→ Klaar voor Fase 2: Refactor + Dockerizen**

### TTS Keuze (afgerond)

**Gekozen:** Chatterbox Multilingual (D008)
- Nederlands native support
- Emotie via `exaggeration` parameter
- ~1-2s latency per zin
- Aparte conda env: `nerdcarx-tts`

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
| 2026-01-11 | TTS: Chatterbox Multilingual gekozen (D008) |
| 2026-01-11 | TTS service geïmplementeerd (port 8250) |
| 2026-01-11 | Orchestrator TTS integratie compleet |
| 2026-01-11 | VAD audio playback + timing per component |
| 2026-01-11 | End-to-end test compleet (zie TESTPLAN.md) |

---

[← Terug naar README](../README.md)
