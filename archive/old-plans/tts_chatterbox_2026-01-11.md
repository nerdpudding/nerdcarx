# Plan: TTS Integratie met Chatterbox

**Datum:** 2026-01-11
**Status:** In review
**Beslissing ID:** D008 (nieuw)

---

## Doel

Text-to-Speech toevoegen aan NerdCarX met **Chatterbox Multilingual** voor Nederlandse spraaksynthese met emotie-expressie.

---

## Huidige Status

- [x] Conda env `nerdcarx-tts` aangemaakt
- [x] `chatterbox-tts` geïnstalleerd
- [x] Test script werkt - Nederlandse generatie OK
- [x] Draait op GPU (~52-55 it/s, ~1-2s per zin)

---

## Research Resultaten

### Gekozen: Chatterbox Multilingual
- **Model:** `ResembleAI/chatterbox` (500M parameters)
- **Nederlands:** Native support (language_id="nl")
- **Emotie:** `exaggeration` parameter (0.25-2.0, default 0.5)
- **Latency:** ~1-2s per zin op RTX 4090
- **Licentie:** MIT
- **Demo:** https://resemble-ai.github.io/chatterbox_demopage/

### Voice Cloning Opties (voor later)
```python
# Zero-shot cloning met reference audio (10+ sec WAV)
wav = model.generate(
    text="Hallo",
    language_id="nl",
    audio_prompt_path="reference.wav"
)
```

### Alternatieven onderzocht
| Model | Reden afgewezen |
|-------|-----------------|
| Kokoro | Geen Nederlands |
| Fish Speech | Licentie restricties |
| Coqui XTTS | Niet meer actief ontwikkeld |
| Piper | Minder expressief |

---

## Technische Details

### Parameters voor emotie-koppeling

| Parameter | Range | Default | NerdCarX gebruik |
|-----------|-------|---------|------------------|
| `exaggeration` | 0.25-2.0 | 0.5 | Map naar emotie intensiteit |
| `cfg_weight` | 0.2-1.0 | 0.5 | Lager voor expressief |
| `temperature` | 0.05-5.0 | 0.8 | Standaard houden |

**Emotie → Exaggeration mapping concept:**
```python
EMOTION_EXAGGERATION = {
    "neutral": 0.5,
    "happy": 0.7,
    "excited": 0.9,
    "sad": 0.6,
    "angry": 0.8,
    "tired": 0.3,
    "bored": 0.3,
    # etc.
}
```

### Voice Reference
- Minimaal 10 seconden audio nodig
- WAV format
- Moet Nederlands zijn voor beste resultaat

---

## Installatie

### Optie: Aparte Conda Environment (aanbevolen)

Dependencies zijn specifiek (torch==2.6.0), kan conflicteren met nerdcarx-vad.

```bash
# 1. Nieuwe environment
conda create -n nerdcarx-tts python=3.11 -y
conda activate nerdcarx-tts

# 2. Install chatterbox
pip install chatterbox-tts

# 3. Test installatie
python -c "from chatterbox.mtl_tts import ChatterboxMultilingualTTS; print('OK')"
```

**VRAM check:** Model download bij eerste gebruik (~2GB model files)

---

## Implementatie Stappen

### Stap 1: TTS README ✅
- [x] Maak `fase1-desktop/tts/README.md`
- [x] Documenteer voice cloning, parameters, emotie mapping

### Stap 2: TTS Service (FastAPI)
- [ ] Maak `fase1-desktop/tts/tts_service.py`
- [ ] Endpoints:
  - `POST /synthesize` - text + emotion → audio bytes
  - `GET /health`
- [ ] Model loaded at startup (warm)
- [ ] Port: 8250

### Stap 3: Orchestrator Integratie

**BELANGRIJK: Function calls NIET naar TTS!**

Huidige flow (orchestrator/main.py):
```python
# Line 573: content is al geschoond van function calls
content, function_calls = parse_text_tool_calls(content)

# Line 595-605: Response heeft gescheiden velden
return ChatResponse(
    response=content,           # ← SCHONE TEKST (naar TTS)
    function_calls=...,         # ← APART (niet naar TTS)
    emotion={...}               # ← EMOTIE INFO (voor TTS exaggeration)
)
```

Toevoegen aan orchestrator:
- [ ] TTS service aanroepen NA LLM response
- [ ] Alleen `content` sturen (niet function_calls)
- [ ] `emotion["current"]` mappen naar `exaggeration` parameter
- [ ] Audio bytes teruggeven in response

### Stap 4: Config uitbreiden
- [ ] TTS settings in `config.yml`
- [ ] Emotie → exaggeration mapping

### Stap 5: VAD Audio Playback (later)
- [ ] Audio ontvangen in VAD client
- [ ] Afspelen via speakers

---

## Folder Structuur

```
fase1-desktop/tts/
├── README.md              # Documentatie
├── test_chatterbox.py     # Eerste test script
├── tts_service.py         # FastAPI service
├── voice_reference.wav    # Nederlandse stem referentie
└── requirements.txt       # Dependencies (optioneel)
```

---

## TTS Service API

```
POST /synthesize
Request: { "text": "...", "emotion": "happy" }
Response: audio/wav bytes

GET /health
Response: { "status": "ok", "model": "chatterbox-multilingual" }
```

---

## Verificatie

1. **TTS service standalone:**
   ```bash
   conda activate nerdcarx-tts
   cd fase1-desktop/tts
   uvicorn tts_service:app --port 8250

   # Test:
   curl -X POST http://localhost:8250/synthesize \
     -H "Content-Type: application/json" \
     -d '{"text": "Hallo, ik ben NerdCarX", "emotion": "happy"}' \
     --output test.wav
   # → test.wav speelt af
   ```

2. **Orchestrator + TTS:**
   ```bash
   # Start beide services, dan:
   curl -X POST http://localhost:8200/conversation \
     -H "Content-Type: application/json" \
     -d '{"message": "Hallo", "conversation_id": "test"}'
   # → Response bevat audio_base64 veld
   ```

3. **VAD end-to-end:**
   ```bash
   python vad_conversation.py
   # Spreek → response wordt afgespeeld via speakers
   ```

---

## Config Uitbreiding (config.yml)

```yaml
tts:
  url: "http://localhost:8250"
  model: "chatterbox-multilingual"
  language: "nl"
  voice_reference: "tts/voice_reference.wav"
  default_exaggeration: 0.5
  emotion_mapping:
    neutral: 0.5
    happy: 0.7
    excited: 0.9
    sad: 0.6
    angry: 0.8
    tired: 0.3
```

---

## Scope

**Wel:**
- Chatterbox Multilingual installeren en testen
- Nederlandse spraaksynthese
- Emotie → exaggeration mapping
- Basis TTS service

**Niet (later):**
- Audio streaming naar Pi
- Voice cloning experimenten
- Docker containerization (Fase 2)

---

## Referenties

- Chatterbox repo: `original_chatterbox-REFERENCE/`
- HuggingFace: https://huggingface.co/ResembleAI/chatterbox
- Demo: https://resemble-ai.github.io/chatterbox_demopage/
