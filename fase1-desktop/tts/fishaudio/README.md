# Fish Audio S1-mini - Test Setup

**Doel:** Evalueren of Fish Audio S1-mini een sneller alternatief is voor Chatterbox
**Model:** fishaudio/openaudio-s1-mini (0.5B parameters)
**Verwachte latency:** 200-500ms (met --compile)

---

## Features

- **Nederlands ondersteund** (en 12+ andere talen)
- **Emotie markers** in tekst: `(excited)`, `(sad)`, `(angry)`, etc.
- **Voice cloning** met 10-30s reference audio
- **Streaming** support
- **#1 op TTS-Arena2** benchmark

---

## Installatie

### Stap 1: Model downloaden

```bash
cd /home/rvanpolen/vibe_claude_kilo_cli_exp/nerdcarx/original_fish-speech-REFERENCE

# Download model (3.4 GB)
git lfs install
git clone https://huggingface.co/fishaudio/openaudio-s1-mini checkpoints/openaudio-s1-mini
```

### Stap 2: Server starten

```bash
cd /home/rvanpolen/vibe_claude_kilo_cli_exp/nerdcarx/original_fish-speech-REFERENCE

# Start API server (niet WebUI)
docker run --gpus device=0 \
    --name fish-tts \
    -v $(pwd)/checkpoints:/app/checkpoints \
    -e COMPILE=1 \
    -p 8250:8080 \
    fishaudio/fish-speech \
    python -m tools.api_server --listen 0.0.0.0:8080
```

Eerste start duurt 2-5 minuten (compile). Daarna ~200-500ms per request.

---

## API Test

```bash
# Basis test
curl -X POST http://localhost:8250/v1/tts \
    -H "Content-Type: application/json" \
    -d '{"text": "Hallo, ik ben NerdCarX. Hoe kan ik je helpen?", "format": "wav"}' \
    --output test.wav

aplay test.wav

# Met emotie
curl -X POST http://localhost:8250/v1/tts \
    -H "Content-Type: application/json" \
    -d '{"text": "(excited) Hallo! Ik ben zo blij je te zien!", "format": "wav"}' \
    --output test_excited.wav
```

---

## Emotie Markers

Voeg toe aan begin van tekst:

**Basis emoties:**
```
(angry) (sad) (excited) (surprised) (satisfied) (delighted)
(scared) (worried) (upset) (nervous) (frustrated) (depressed)
(empathetic) (embarrassed) (disgusted) (moved) (proud) (relaxed)
(grateful) (confident) (interested) (curious) (confused) (joyful)
```

**Toon:**
```
(in a hurry tone) (shouting) (screaming) (whispering) (soft tone)
```

**Geluidseffecten:**
```
(laughing) (chuckling) (sobbing) (crying loudly) (sighing)
```

---

## Test Script

Na server start:

```bash
cd /home/rvanpolen/vibe_claude_kilo_cli_exp/nerdcarx/fase1-desktop/tts/fishaudio
python test_fishaudio_nl.py
```

---

## Verwachte Resultaten

### Goed scenario
- Nederlands: Verstaanbaar, natuurlijk
- Latency: <500ms
- Emoties: Merkbaar verschil

### Slecht scenario
- Latency: >1000ms constant
- Dan: Probeer Piper als backup

---

## Links

- GitHub: https://github.com/fishaudio/fish-speech
- HuggingFace: https://huggingface.co/fishaudio/openaudio-s1-mini
- Docs: https://docs.fish.audio/

---

*Aangemaakt: 2026-01-11*
