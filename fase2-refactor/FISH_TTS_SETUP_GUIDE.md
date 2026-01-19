# Fish Audio TTS - Standalone Setup Guide

Handleiding om Fish Audio TTS (Text-to-Speech) standalone te draaien via Docker.
Werkt op systemen met of zonder NVIDIA GPU.

---

## Inhoudsopgave

1. [Over het Model](#over-het-model)
2. [Vereisten](#vereisten)
3. [Stap 1: Repository Clonen](#stap-1-repository-clonen)
4. [Stap 2: Directory Structuur Aanmaken](#stap-2-directory-structuur-aanmaken)
5. [Stap 3: Model Downloaden](#stap-3-model-downloaden-openaudio-s1-mini)
6. [Stap 4: Reference Audio (Voice Clone)](#stap-4-reference-audio-voice-clone)
7. [Stap 5: Docker Compose](#stap-5-docker-compose)
8. [Stap 6: Fish Audio TTS Starten](#stap-6-fish-audio-tts-starten)
9. [Stap 7: Health Check](#stap-7-health-check)
10. [Stap 8: Testen!](#stap-8-testen)
11. [API Reference](#api-reference)
12. [Troubleshooting](#troubleshooting)
13. [Directory Structuur Overzicht](#directory-structuur-overzicht)
14. [Meer Informatie](#meer-informatie)

---

## Over het Model

Deze guide gebruikt **OpenAudio S1-mini** (0.5B parameters) - een open-source model dat je lokaal kunt draaien.

**Belangrijk verschil met Fish Audio Cloud:**
| Feature | S1-mini (lokaal) | S1 (cloud/proprietary) |
|---------|------------------|------------------------|
| Voice cloning | Ja | Ja |
| Emotie markers `(happy)`, `(sad)` etc. | **Nee** | Ja |
| Tone markers `(whispering)` etc. | **Nee** | Ja |
| Gratis | Ja | Nee (betaald) |
| Privacy | Volledig lokaal | Data naar cloud |

S1-mini is perfect voor voice cloning - je kunt elke stem klonen met een kort audio fragment. Emotie/tone markers werken alleen via de betaalde Fish Audio cloud API (fish.audio).

## Vereisten

### Minimum systeemeisen

| Component | Minimum | Aanbevolen |
|-----------|---------|------------|
| RAM | 8 GB | 16 GB |
| Schijfruimte | 5 GB vrij | 10 GB vrij |
| CPU | 4 cores | 8+ cores |
| GPU | Niet vereist | NVIDIA met 6GB+ VRAM |

### Software vereisten

Je hebt de volgende software nodig:

| Software | Waarom nodig | Installatie |
|----------|--------------|-------------|
| **Docker** | Container runtime | Zie onder |
| **Docker Compose** | Multi-container orchestratie | Inbegrepen bij Docker Desktop |
| **Git** | Repository clonen | Zie onder |
| **Git LFS** | Grote bestanden downloaden | Zie onder |
| **curl** | API testen | Meestal al geïnstalleerd |

### Docker installeren

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
# Docker installeren
curl -fsSL https://get.docker.com | sudo sh

# Jezelf toevoegen aan docker groep (herstart terminal daarna)
sudo usermod -aG docker $USER

# Testen
docker --version
docker compose version
```
</details>

<details>
<summary><b>macOS</b></summary>

Download en installeer [Docker Desktop voor Mac](https://docs.docker.com/desktop/install/mac-install/)

```bash
# Na installatie, test:
docker --version
docker compose version
```
</details>

<details>
<summary><b>Windows</b></summary>

1. Installeer [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) (Windows Subsystem for Linux)
2. Download en installeer [Docker Desktop voor Windows](https://docs.docker.com/desktop/install/windows-install/)
3. Zorg dat WSL2 backend is ingeschakeld in Docker Desktop settings

```powershell
# Test in PowerShell of WSL terminal:
docker --version
docker compose version
```
</details>

### Git en Git LFS installeren

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
sudo apt update
sudo apt install git git-lfs
git lfs install
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
# Met Homebrew
brew install git git-lfs
git lfs install
```
</details>

<details>
<summary><b>Windows</b></summary>

Download en installeer:
1. [Git voor Windows](https://git-scm.com/download/win)
2. [Git LFS](https://git-lfs.com/)

```powershell
git lfs install
```
</details>

### Controleer je installatie

```bash
# Alle vereisten checken
docker --version          # Docker version 20+ verwacht
docker compose version    # Docker Compose version v2+ verwacht
git --version             # git version 2+ verwacht
git lfs --version         # git-lfs/3+ verwacht
```

---

## Stap 1: Repository Clonen

```bash
git clone https://github.com/[JOUW-USERNAME]/nerdcarx.git
cd nerdcarx/fase2-refactor
```

## Stap 2: Directory Structuur Aanmaken

Fish Audio verwacht bepaalde directories. Maak deze aan:

```bash
# Maak de nodige directories
mkdir -p tts/fishaudio/checkpoints
mkdir -p tts/fishaudio/references
mkdir -p tts/inductor-cache
```

## Stap 3: Model Downloaden (openaudio-s1-mini)

Het model (~3.5GB) wordt gedownload van HuggingFace:

```bash
cd tts/fishaudio/checkpoints

# Clone het model (heeft Git LFS nodig)
git lfs install
git clone https://huggingface.co/fishaudio/openaudio-s1-mini

cd ../../..  # Terug naar fase2-refactor
```

**Alternatief zonder Git LFS** (handmatig):
1. Ga naar: https://huggingface.co/fishaudio/openaudio-s1-mini/tree/main
2. Download deze bestanden naar `tts/fishaudio/checkpoints/openaudio-s1-mini/`:
   - `config.json`
   - `model.pth` (~1.7GB)
   - `codec.pth` (~1.9GB)
   - `special_tokens.json`
   - `tokenizer.tiktoken`

## Stap 4: Reference Audio (Voice Clone)

Fish Audio kloont een stem op basis van "reference audio". De repo bevat al een voorbeeld (`dutch2`), maar je kunt ook je eigen stem toevoegen.

### Optie A: Gebruik de meegeleverde reference (dutch2)

De repo bevat al een Nederlandse reference voice in `tts/fishaudio/references/dutch2/`. Deze kun je direct gebruiken - geen extra actie nodig.

### Optie B: Eigen stem opnemen

Wil je je eigen stem klonen? Maak dan:
1. **Een audio bestand** (`.mp3` of `.wav`, 10-30 seconden)
2. **Een transcriptie** (`.lab` bestand met exact de gesproken tekst)

```bash
# Maak een directory voor je voice reference
mkdir -p tts/fishaudio/references/mijnvoice

# Kopieer je audio bestand
cp /pad/naar/jouw-opname.mp3 tts/fishaudio/references/mijnvoice/reference.mp3

# Maak transcriptie (EXACT wat je zegt in de audio)
echo "Dit is de tekst die ik in mijn audio heb ingesproken, woord voor woord." > tts/fishaudio/references/mijnvoice/reference.lab
```

**Tips voor een goede voice clone:**
- Spreek duidelijk en in normaal tempo
- Vermijd achtergrondgeluid (stil kantoor/kamer)
- 10-30 seconden audio is ideaal
- De transcriptie moet EXACT overeenkomen met wat je zegt
- Neem op met een redelijke microfoon (telefoon is vaak goed genoeg)

## Stap 5: Docker Compose

De repo bevat een kant-en-klaar `docker-compose.tts-standalone.yml` bestand voor CPU-only systemen.

**Heb je een NVIDIA GPU?** Dan kun je een aangepaste versie maken:

<details>
<summary>GPU versie (klik om te openen)</summary>

Maak `docker-compose.tts-gpu.yml`:

```yaml
# Fish Audio TTS - Met GPU
services:
  tts:
    image: fishaudio/fish-speech:latest
    container_name: fish-tts
    ports:
      - "8250:8080"
    volumes:
      - ./tts/fishaudio/checkpoints:/app/checkpoints:ro
      - ./tts/fishaudio/references:/app/references
      - ./tts/inductor-cache:/app/inductor-cache
    environment:
      - TORCHINDUCTOR_CACHE_DIR=/app/inductor-cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    entrypoint: uv
    command: run tools/api_server.py --listen 0.0.0.0:8080 --compile
    restart: unless-stopped
```

Start met: `docker compose -f docker-compose.tts-gpu.yml up -d`

</details>

## Stap 6: Fish Audio TTS Starten

```bash
# Start de container (CPU versie)
docker compose -f docker-compose.tts-standalone.yml up -d

# Bekijk de logs (eerste keer duurt even door model loading)
docker compose -f docker-compose.tts-standalone.yml logs -f
```

**Eerste startup:** Duurt 2-5 minuten (model laden, optioneel compileren).

Wacht tot je in de logs ziet:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

## Stap 7: Health Check

```bash
curl http://localhost:8250/v1/health
```

Verwachte output: `{"status":"ok"}`

## Stap 8: Testen!

### Test met curl:

```bash
# Test met de meegeleverde dutch2 voice
curl -X POST http://localhost:8250/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hallo, dit is een test van Fish Audio!",
    "reference_id": "dutch2"
  }' \
  --output test_output.wav

# Speel af (Linux)
aplay test_output.wav

# Of op Mac
# afplay test_output.wav

# Test met je eigen voice (als je die hebt aangemaakt)
curl -X POST http://localhost:8250/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Dit is mijn eigen stem!",
    "reference_id": "mijnvoice"
  }' \
  --output mijn_stem_test.wav
```

### Beschikbare references bekijken:

```bash
curl http://localhost:8250/v1/models
```

## API Reference

### POST /v1/tts

Genereer spraak van tekst.

```json
{
  "text": "Je tekst hier",
  "reference_id": "dutch2",
  "temperature": 0.5,
  "top_p": 0.6,
  "format": "wav"
}
```

Parameters:
- `text`: De tekst om te spreken
- `reference_id`: Naam van de reference directory (bijv. `dutch2` of je eigen `mijnvoice`)
- `temperature`: 0.1-1.0, hogere waarde = meer variatie (default: 0.5)
- `top_p`: 0.1-1.0, nucleus sampling (default: 0.6)
- `format`: `wav` of `mp3`

## Troubleshooting

### Container start niet
```bash
# Check logs
docker compose -f docker-compose.tts-standalone.yml logs

# Check of model bestanden aanwezig zijn
ls -la tts/fishaudio/checkpoints/openaudio-s1-mini/
```

### "No such reference_id" fout
```bash
# Check of reference directory correct is
ls -la tts/fishaudio/references/

# Directory moet bevatten:
# - reference.mp3 (of .wav)
# - reference.lab (transcriptie)
```

### Traag op CPU
CPU mode is aanzienlijk trager (~10-30x) dan GPU. Overweeg:
- Kortere teksten per request
- Een cloud GPU (bijv. vast.ai, runpod.io)

### Out of memory
- Verlaag `--max-batch-size 1` in de command
- Sluit andere applicaties

## Directory Structuur Overzicht

```
fase2-refactor/
├── docker-compose.tts-standalone.yml  # Standalone TTS config (CPU)
└── tts/
    ├── fishaudio/
    │   ├── checkpoints/
    │   │   └── openaudio-s1-mini/     # Het model (~3.5GB)
    │   │       ├── config.json
    │   │       ├── model.pth          # ~1.7GB
    │   │       ├── codec.pth          # ~1.9GB
    │   │       ├── special_tokens.json
    │   │       └── tokenizer.tiktoken
    │   └── references/
    │       ├── dutch2/                # Meegeleverde Nederlandse stem
    │       │   ├── reference.mp3
    │       │   └── reference.lab
    │       └── mijnvoice/             # (optioneel) Je eigen stem
    │           ├── reference.mp3
    │           └── reference.lab
    └── inductor-cache/                # PyTorch cache (auto-generated)
```

## Meer Informatie

- Fish Speech GitHub: https://github.com/fishaudio/fish-speech
- Model pagina: https://huggingface.co/fishaudio/openaudio-s1-mini
- Fish Audio Playground: https://fish.audio (om online te testen)
