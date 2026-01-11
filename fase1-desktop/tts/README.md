# TTS - Chatterbox Multilingual

Text-to-Speech voor NerdCarX met Nederlandse spraaksynthese en emotie-expressie.

## Model

**Chatterbox Multilingual** (ResembleAI)
- 500M parameters
- 23 talen inclusief Nederlands
- Zero-shot voice cloning
- Emotie controle via `exaggeration` parameter

## Installatie

```bash
# Aparte conda environment (torch==2.6.0 specifiek)
conda create -n nerdcarx-tts python=3.11 -y
conda activate nerdcarx-tts
pip install chatterbox-tts
```

## Gebruik

### Basis generatie

```python
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torchaudio as ta

model = ChatterboxMultilingualTTS.from_pretrained(device="cuda")

wav = model.generate(
    text="Hallo, ik ben NerdCarX",
    language_id="nl"
)
ta.save("output.wav", wav, model.sr)
```

### Met emotie parameters

```python
wav = model.generate(
    text="Wat leuk dat je er bent!",
    language_id="nl",
    exaggeration=0.8,  # Meer expressief (0.25-2.0)
    cfg_weight=0.3     # Langzamer, dramatischer (0.2-1.0)
)
```

### Voice cloning (zero-shot)

```python
# Reference audio: minimaal 10 seconden, WAV, Nederlands
wav = model.generate(
    text="Hallo!",
    language_id="nl",
    audio_prompt_path="voice_reference.wav"
)
```

## Parameters

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `exaggeration` | 0.25-2.0 | 0.5 | Emotie intensiteit |
| `cfg_weight` | 0.2-1.0 | 0.5 | Pacing (lager = langzamer) |
| `temperature` | 0.05-5.0 | 0.8 | Variatie |

### Emotie mapping (NerdCarX)

| Emotie | exaggeration | cfg_weight |
|--------|--------------|------------|
| neutral | 0.5 | 0.5 |
| happy | 0.7 | 0.4 |
| excited | 0.9 | 0.3 |
| sad | 0.6 | 0.5 |
| angry | 0.8 | 0.4 |
| tired | 0.3 | 0.6 |
| bored | 0.3 | 0.6 |
| curious | 0.6 | 0.5 |

## Service

TTS draait als FastAPI service op port 8250.

```bash
conda activate nerdcarx-tts
cd fase1-desktop/tts
uvicorn tts_service:app --port 8250
```

### API

```
GET /health
POST /synthesize
  Body: { "text": "...", "emotion": "happy" }
  Response: audio/wav bytes
```

## Bestanden

```
tts/
├── README.md              # Dit bestand
├── test_chatterbox.py     # Test script
├── tts_service.py         # FastAPI service
├── test_output/           # Test output folder
└── voice_reference.wav    # (optioneel) Nederlandse stem
```

## Performance

- Latency: ~1-2s per zin op RTX 4090
- Sampling speed: ~52-55 it/s
- VRAM: ~4-6GB (model + inference)

## Referenties

- [HuggingFace](https://huggingface.co/ResembleAI/chatterbox)
- [Demo](https://resemble-ai.github.io/chatterbox_demopage/)
- [GitHub](https://github.com/resemble-ai/chatterbox)
