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
- TTS via Fish Audio S1-mini (Docker, port 8250)
- Orchestrator met centrale config + hot reload
- VAD hands-free gesprekken
- Vision via `take_photo` function call
- Emoties via `show_emotion` function call

**Performance:**
- Vision latency: ~5-10s (dubbele LLM call)
- TTS latency: ~1.2s per zin (Fish Audio)
- STT latency: 150-750ms
- LLM latency: 700-1300ms

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
  model: "ministral-3:14b-instruct-2512-q8_0"
  temperature: 0.15    # Officieel
  top_p: 1.0           # Officieel
  repeat_penalty: 1.0  # Officieel

voxtral:
  temperature: 0.0     # Greedy voor transcriptie

tts:  # Fish Audio S1-mini
  url: "http://localhost:8250"
  enabled: true
  reference_id: "dutch2"
  temperature: 0.2     # ultra_consistent
  top_p: 0.5           # ultra_consistent

system_prompt: |
  Je bent de AI van NerdCarX...

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

## Volgende Stappen

### 1. Orchestrator Fish Audio Integratie ✅

De orchestrator is aangepast voor Fish Audio API:
- Config loading met reference_id, temperature, top_p, format
- `synthesize_speech()` roept `/v1/tts` aan
- Health check via `/v1/health`
- Hot reload werkt met nieuwe TTS variabelen

### 2. End-to-end Testing ⏳

- [ ] Fish Audio Docker starten + reference uploaden
- [ ] Volledige loop testen: spraak → STT → LLM → TTS → audio
- [ ] Timing per component verifiëren

### 3. Fase 1 Afronden

- [x] TTS latency opgelost (D009 - Fish Audio ~1.2s vs Chatterbox 5-20s)
- [x] Orchestrator Fish Audio integratie
- [x] End-to-end test (zie `tts/test_output/full_flow_test_2026-01-11.md`)

### 4. Open Issues / Wensen

**TTS Kwaliteit:**
- [ ] Parameters vergelijken: waarom klinkt het Engelser dan in test script?
- [ ] Kortere zinnen genereren in LLM prompt?

**STT:**
- [ ] Voxtral negeert soms `language: 'nl'` - transcribeert Engels

**Playback Interrupt (wens):**
- [ ] Playback onderbreken tijdens afspelen (voice-based of keyboard)
- Opties: VAD tijdens playback, keyboard shortcut, of wake word
- Audio echo is uitdaging bij voice-based oplossing

**→ Daarna: Fase 2: Refactor + Dockerizen**

---

## TTS Keuze (D009)

**Gekozen:** Fish Audio S1-mini (vervangt Chatterbox)

| Aspect | Waarde |
|--------|--------|
| Model | fishaudio/openaudio-s1-mini |
| Latency | ~1.2s per zin |
| Nederlands | Via reference audio (dutch2) |
| Parameters | temperature=0.2, top_p=0.5 (ultra_consistent) |

**Geteste alternatieven:**
| Model | Latency | Status |
|-------|---------|--------|
| Chatterbox | 5-20s | ❌ Te traag |
| VibeVoice | 1-2s | ❌ Belgisch accent |
| Coqui XTTS-v2 | - | ❌ Project dood |
| Fish Audio | ~1.2s | ✅ GEKOZEN |

**Reference audio:** `tts/fishaudio/elevenreference/reference2_NL_FM.mp3`

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
| 2026-01-11 | Documentatie bijgewerkt |
| 2026-01-11 | Orchestrator aangepast voor Fish Audio API |
| 2026-01-11 | End-to-end test uitgevoerd (resultaten in tts/test_output/) |

---

[← Terug naar README](../README.md)
