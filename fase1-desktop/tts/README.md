# TTS - Fish Audio S1-mini

Text-to-Speech voor NerdCarX met Nederlandse spraaksynthese.

> **Opmerking:** Fish Audio vervangt Chatterbox vanwege betere latency (~1.2s vs 5-20s). Zie [D009](../../DECISIONS.md) voor details.

## Model

**Fish Audio S1-mini** (fishaudio/openaudio-s1-mini)
- 0.5B parameters
- #1 op TTS-Arena2 benchmark
- Voice cloning via reference audio
- Emotie markers ondersteund

## Quick Start

### 1. Model downloaden (eenmalig)

```bash
cd /home/rvanpolen/vibe_claude_kilo_cli_exp/nerdcarx/original_fish-speech-REFERENCE

git lfs install
git clone https://huggingface.co/fishaudio/openaudio-s1-mini checkpoints/openaudio-s1-mini
```

### 2. Docker starten

```bash
cd /home/rvanpolen/vibe_claude_kilo_cli_exp/nerdcarx/original_fish-speech-REFERENCE

docker run -d --gpus device=0 --name fish-tts \
    -v $(pwd)/checkpoints:/app/checkpoints \
    -v $(pwd)/references:/app/references \
    -p 8250:8080 --entrypoint uv \
    fishaudio/fish-speech \
    run tools/api_server.py --listen 0.0.0.0:8080 --compile
```

> **Eerste start:** 2-5 minuten (compile). Daarna ~1.2s per request.
>
> **References zijn persistent:** De `dutch2` reference is al aanwezig in `references/dutch2/`.
> Geen upload nodig na container restart.

### 3. Testen

```bash
curl -X POST http://localhost:8250/v1/tts \
    -H "Content-Type: application/json" \
    -d '{"text": "Hallo, ik ben NerdCarX!", "reference_id": "dutch2", "temperature": 0.2, "top_p": 0.5, "format": "wav"}' \
    --output test.wav

aplay test.wav
```

### Check references

```bash
curl http://localhost:8250/v1/references/list
# Moet "dutch2" tonen
```

## Parameters

### Geteste configuraties

| Configuratie | temperature | top_p | Omschrijving |
|--------------|-------------|-------|--------------|
| **ultra_consistent** | **0.2** | **0.5** | **GEKOZEN - beste Nederlandse uitspraak** |
| very_consistent | 0.3 | 0.6 | Iets natuurlijker, kleine variatie |

> Lagere waarden = consistenter maar minder natuurlijk
> Hogere waarden = meer variatie maar risico op accent drift

### Emotie markers

Fish Audio ondersteunt emotie markers in de tekst:

```
(happy) Wat leuk!
(sad) Dat is jammer.
(excited) Dit is geweldig!
(angry) Ik ben niet blij.
(whisper) Dit is een geheim.
```

## API

**Endpoint:** `http://localhost:8250/v1/tts`

### Request

```json
{
    "text": "Hallo, hoe gaat het?",
    "reference_id": "dutch2",
    "temperature": 0.2,
    "top_p": 0.5,
    "format": "wav"
}
```

### Response

Audio bytes (WAV format)

### Health check

```bash
curl http://localhost:8250/v1/health
```

## Folder Structuur

### Waarom twee locaties?

| Locatie | Doel |
|---------|------|
| `original_fish-speech-REFERENCE/` | Gecloned Fish Audio repo + model + references (Docker mount) |
| `fase1-desktop/tts/` | Onze project TTS code, docs, tests |

### Overzicht

```
nerdcarx/
│
├── original_fish-speech-REFERENCE/      # FISH AUDIO REPO (gecloned)
│   ├── checkpoints/
│   │   └── openaudio-s1-mini/           # Model (3.4GB via git lfs)
│   └── references/                       # PERSISTENT REFERENCES (Docker mount)
│       └── dutch2/                       # Nederlandse stem
│           ├── reference.mp3
│           └── reference.lab
│
└── fase1-desktop/
    └── tts/                              # ONZE TTS CODE
        ├── README.md                     # Dit bestand
        ├── test_output/                  # Test audio output
        └── fishaudio/
            ├── elevenreference/          # Bron bestanden (ElevenLabs export)
            │   ├── reference1_NL_FM.mp3
            │   ├── reference1_NL_FM.txt
            │   ├── reference2_NL_FM.mp3  # Bron voor dutch2
            │   └── reference2_NL_FM.txt
            └── test_parameters.py        # Parameter test script
```

### Docker Mounts

De Fish Audio container mount twee folders:

```bash
-v $(pwd)/checkpoints:/app/checkpoints   # Model
-v $(pwd)/references:/app/references     # Voice references (persistent!)
```

Waarbij `$(pwd)` = `original_fish-speech-REFERENCE/`

## Performance

| Metric | Waarde |
|--------|--------|
| Latency | ~1.2s per zin |
| Model size | 0.5B parameters |
| VRAM | ~4-6GB |
| Compile time | 2-5 min (eenmalig) |

### Vergelijking met alternatieven

| Model | Latency | Nederlands | Status |
|-------|---------|------------|--------|
| **Fish Audio S1-mini** | **~1.2s** | ✅ (via reference) | **ACTIEF** |
| Chatterbox | 5-20s | ✅ | ❌ Te traag |
| VibeVoice | 1-2s | ❌ Belgisch | ❌ Kwaliteit |
| Piper | <100ms | ✅ | Backup optie |

## Troubleshooting

### Container bestaat al

```bash
docker stop fish-tts && docker rm fish-tts
# Dan opnieuw docker run ...
```

### Server start niet

Controleer of de checkpoints correct zijn gedownload:

```bash
ls original_fish-speech-REFERENCE/checkpoints/openaudio-s1-mini/
# Moet meerdere bestanden tonen (.safetensors, config.json, etc.)
```

### Reference niet gevonden

Controleer of de references folder correct gemount is:

```bash
docker exec fish-tts ls /app/references/dutch2/
# Moet reference.mp3 en reference.lab tonen
```

### Nieuwe reference toevoegen

Als je een nieuwe reference wilt toevoegen:

```bash
# 1. Maak folder aan
mkdir -p original_fish-speech-REFERENCE/references/{nieuwe_id}

# 2. Kopieer audio bestand (mp3/wav)
cp jouw_audio.mp3 original_fish-speech-REFERENCE/references/{nieuwe_id}/reference.mp3

# 3. Maak .lab bestand met de gesproken tekst
echo "De tekst die in de audio wordt gesproken" > original_fish-speech-REFERENCE/references/{nieuwe_id}/reference.lab

# 4. Herstart container (of hij pikt het automatisch op)
```

## Referenties

- [Fish Audio GitHub](https://github.com/fishaudio/fish-speech)
- [HuggingFace Model](https://huggingface.co/fishaudio/openaudio-s1-mini)
- [Fish Audio Docs](https://docs.fish.audio/)
- [D009 Beslissing](../../DECISIONS.md)

---

*Laatst bijgewerkt: 2026-01-11 (References nu persistent via volume mount)*
