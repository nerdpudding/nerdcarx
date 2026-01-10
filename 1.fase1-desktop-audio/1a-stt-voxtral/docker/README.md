# Voxtral Mini - Docker Setup

> **Status:** ✅ Werkend op RTX 5070 Ti (GPU1)

---

## Vereisten

- Ubuntu met Docker
- NVIDIA GPU met ~16 GB VRAM (5070 Ti) of ~12 GB (met lagere cache)
- NVIDIA Container Toolkit
- ~15 GB schijfruimte voor model

---

## Quick Start

```bash
# Bouw custom image (eerste keer)
docker compose build

# Start
docker compose up -d

# Check logs
docker compose logs -f

# Stop
docker compose down
```

---

## Testen

### 1. Check health

```bash
curl http://localhost:8150/health
```

### 2. Microfoon zoeken

```bash
arecord -l
```

Output voorbeeld:
```
card 5: Mini [Razer Seiren Mini], device 0: USB Audio [USB Audio]
```

### 3. Audio opnemen

```bash
# Pas hw:X,0 aan naar jouw card nummer
# Mono, 16-bit, 44.1kHz, 5 seconden
arecord -D hw:5,0 -d 5 -f S16_LE -r 44100 -c 1 -t wav test.wav
```

### 4. Transcriptie testen

```bash
curl -X POST http://localhost:8150/v1/audio/transcriptions \
    -H "Content-Type: multipart/form-data" \
    -F "file=@test.wav" \
    -F "model=mistralai/Voxtral-Mini-3B-2507"
```

Verwachte output:
```json
{"text":"Je gesproken tekst hier.","usage":{"type":"duration","seconds":5}}
```

---

## Voxtral Capabilities

### Wat Voxtral WEL kan

| Feature | Status | Notes |
|---------|--------|-------|
| **Transcriptie** | ✅ Werkt | Zeer goede kwaliteit, beter dan Whisper |
| **Meertalig** | ✅ Werkt | 8 talen incl. Nederlands |
| **Audio Q&A** | ✅ Werkt | Vragen over audio content |
| **Samenvatting** | ✅ Werkt | Audio samenvatten |
| **Function calling** | ✅ Werkt | Acties triggeren vanuit spraak |
| **Lange audio** | ✅ Werkt | Tot 30 min transcriptie, 40 min understanding |

### Wat Voxtral NIET kan (nog niet)

| Feature | Status | Notes |
|---------|--------|-------|
| **Emotie detectie** | ❌ Niet ondersteund | Op roadmap ("coming soon") |
| **Leeftijd detectie** | ❌ Niet ondersteund | Op roadmap |
| **Speaker diarization** | ❌ Niet ingebouwd | Aparte tool nodig |

> **Bron:** [Mistral Voxtral Announcement](https://mistral.ai/news/voxtral)

---

## Aanbevolen Parameters

| Taak | Temperature | Top P | Notes |
|------|-------------|-------|-------|
| **Transcriptie** | `0.0` | - | Deterministisch, beste accuracy |
| **Audio Q&A / Understanding** | `0.2` | `0.95` | Lichte creativiteit toegestaan |

> **Bron:** [HuggingFace Model Card](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507)

---

## Geavanceerde Tests

### Audio Q&A (Chat over audio)

Voxtral kan vragen beantwoorden over audio content (bijv. samenvatting, taal detectie, inhoudelijke vragen).

**Stap 1:** Maak een test bestand aan (eenmalig):

```bash
cat > test-audio-qa.sh << 'EOF'
#!/bin/bash
FILE=$1
VRAAG=${2:-"Geef een korte samenvatting van wat er gezegd wordt."}

echo "Audio: $FILE"
echo "Vraag: $VRAAG"
echo ""

B64=$(base64 -w0 "$FILE")

cat > /tmp/request.json << JSONEOF
{
  "model": "mistralai/Voxtral-Mini-3B-2507",
  "temperature": 0.2,
  "top_p": 0.95,
  "max_tokens": 200,
  "messages": [{
    "role": "user",
    "content": [
      {"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64,$B64"}},
      {"type": "text", "text": "$VRAAG"}
    ]
  }]
}
JSONEOF

curl -s -X POST http://localhost:8150/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/request.json | jq -r '.choices[0].message.content'
EOF
chmod +x test-audio-qa.sh
```

**Stap 2:** Test uitvoeren:

```bash
# Samenvatting (default)
./test-audio-qa.sh test.wav

# Specifieke vraag
./test-audio-qa.sh test.wav "In welke taal wordt er gesproken?"
./test-audio-qa.sh test.wav "Hoeveel sprekers hoor je?"
```

### Meertalig (Nederlands)

Voxtral ondersteunt 8 talen waaronder Nederlands (automatische detectie):

```bash
curl -X POST http://localhost:8150/v1/audio/transcriptions \
    -H "Content-Type: multipart/form-data" \
    -F "file=@dutch_audio.wav" \
    -F "model=mistralai/Voxtral-Mini-3B-2507"
```

Optioneel taal forceren:

```bash
curl -X POST http://localhost:8150/v1/audio/transcriptions \
    -H "Content-Type: multipart/form-data" \
    -F "file=@dutch_audio.wav" \
    -F "model=mistralai/Voxtral-Mini-3B-2507" \
    -F "language=nl"
```

### Getest

- [x] Function calling vanuit audio → Werkt! Zie `test-audio/test-function.sh`

### Nog te testen

- [ ] Langere audio fragmenten (>30 sec)
- [ ] Achtergrondgeluid/noise robustness

---

## GPU Configuratie

Huidige setup: **GPU1 (RTX 5070 Ti)**

In `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['1']  # GPU1
          capabilities: [gpu]
```

Om GPU0 (RTX 4090) te gebruiken:
```yaml
device_ids: ['0']
```

---

## VRAM Gebruik

| GPU | Memory Util | VRAM Gebruik |
|-----|-------------|--------------|
| RTX 5070 Ti | 75% | ~15.2 GB |
| RTX 4090 | 90% | ~22.7 GB |

Aanpassen in `docker-compose.yml`:
```yaml
--gpu-memory-utilization 0.75  # of 0.50 voor minder cache
```

---

## vLLM Optimalisaties

### Huidige instellingen (aanbevolen)

| Setting | Waarde | Reden |
|---------|--------|-------|
| `--gpu-memory-utilization` | 0.75 | Balans VRAM/cache op 5070 Ti |
| `--max-model-len` | 4096 | Voldoende voor audio context |
| `--tokenizer_mode mistral` | - | Vereist voor Voxtral |
| `--config_format mistral` | - | Vereist voor Voxtral |
| `--load_format mistral` | - | Vereist voor Voxtral |

### Al automatisch ingeschakeld door vLLM

- **Prefix caching:** Hergebruik van gedeelde prefixes
- **Chunked prefill:** Efficiëntere batch processing
- **Flash Attention:** Snellere attention berekening
- **CUDA Graphs:** Lagere kernel launch overhead

### Optioneel (niet nodig voor STT)

| Setting | Wanneer gebruiken |
|---------|------------------|
| `--enable-prefix-caching` | Al default aan |
| `--speculative-model` | Niet relevant voor STT |
| `--tensor-parallel-size` | Alleen bij multi-GPU voor 1 model |

---

## Troubleshooting

### Container start niet op 5070 Ti

```
ValueError: Free memory on device cuda:0 (12.77/15.44 GiB)...
```

**Fix:** Verlaag `--gpu-memory-utilization` naar 0.70 of 0.75

### Connection reset by peer

Waarschijnlijk eerste request na warmup. Probeer opnieuw.

### Audio dependencies ontbreken

```
ModuleNotFoundError: No module named 'librosa'
```

**Fix:** Rebuild met custom Dockerfile:
```bash
docker compose build --no-cache
```

---

[← Terug naar 1a Plan](../PLAN.md)
