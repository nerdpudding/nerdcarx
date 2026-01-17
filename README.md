# NerdCarX

Een AI-gestuurde robotauto gebaseerd op de PiCar-X, met lokale spraakinteractie, emotie-display en vision capabilities.

## Inhoudsopgave

- [Werkwijze](#werkwijze)
- [Doelstelling](#doelstelling)
- [Concept Samenvatting](#concept-samenvatting)
- [Fasen](#fasen)
- [Repository Structuur](#repository-structuur)
- [Quick Start](#quick-start)
- [Hardware Vereisten](#hardware-vereisten)
- [Status](#status)

> **📐 Architectuur Overzicht:** Zie [`ARCHITECTURE.md`](ARCHITECTURE.md) voor:
> - Waarom deze architectuur en technologie keuzes (design rationale)
> - PiCar-X hardware platform en ingebouwde mogelijkheden
> - Wat onze lokale AI stack toevoegt boven de standaard PiCar-X
> - C4 diagrammen (Context, Container, Component) per fase
> - Huidige status, roadmap en toekomstige uitbreidingen

> **🤖 AI Assistenten:** Zie [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) voor instructies bij het werken met dit project.

---

## Werkwijze

> **Belangrijk:** Dit project hanteert een duidelijke structuur om verwarring te voorkomen.

### Centrale Beslissingen

Alle projectbeslissingen staan op **één plek**: [`DECISIONS.md`](DECISIONS.md)

- Elke keuze krijgt een ID (D001, D002, ...)
- Bevat rationale en alternatieven
- Chronologisch, nooit verwijderen
- **Dit is de bron van waarheid**

### Document Structuur

| Document | Doel | Bijwerken |
|----------|------|-----------|
| `ARCHITECTURE.md` | Architectuur overzicht met C4 diagrammen | Bij grote wijzigingen |
| `DECISIONS.md` | Alle beslissingen | Bij elke keuze |
| `README.md` | Overzicht + huidige fase | Bij fasewissel |
| `archive/` | Afgeronde documenten (read-only) | Nooit |
| `*/README.md` | Overzicht per fase/component | Tijdens die fase |
| `*/TODO.md` | Openstaande punten | Bij nieuwe wensen |

### Waarom zo?

- **Eén bron van waarheid** - geen verwarring over wat actueel is
- **Archief blijft intact** - origineel concept als referentie
- **Minder bijwerken** - alleen DECISIONS.md + actieve PLAN
- **Schaalt** - werkt ook als het project groeit

---

## Doelstelling

Een interactieve AI-gestuurde robotauto bouwen die:
- **Luistert en reageert** via spraak (conversational AI)
- **Emoties toont** op een OLED display
- **Visueel waarneemt** en reageert (camera/vision)
- **Fysiek beweegt** en interacteert

**Kernprincipes:**
- **Local-first**: Alles draait lokaal (geen API kosten, geen rate limiting, privacy)
- **Modulair**: Docker containers, loose coupling, swappable services
- **Desktop-first**: Ontwikkelen en testen op desktop, daarna naar Pi

## Concept Samenvatting

```
                    Desktop Server                              Pi 5 Robot
              ┌────────────────────────┐              ┌────────────────────────┐
              │  Orchestrator (FastAPI)│◄────────────►│  Wake Word (Porcupine) │
              │  STT (Voxtral)         │   WebSocket  │  Audio Capture (Mic)   │
              │  LLM (Ministral 14B)   │     LAN      │  Camera (Vision)       │
              │  TTS (Fish Audio)      │              │  OLED (Emoties)        │
              └────────────────────────┘              │  Motors/Servo's        │
                      GPU Processing                  └────────────────────────┘
```

**Typische interactie:**
1. Gebruiker zegt "Hey robot" (wake word)
2. Pi neemt vraag op en stuurt naar desktop
3. Desktop: STT → LLM → TTS
4. Response + function calls terug naar Pi
5. Pi: speelt audio af, toont emotie, voert bewegingen uit

## Fasen

| Fase | Naam | Beschrijving | Status |
|------|------|--------------|--------|
| 0 | [Concept](archive/0.concept/) | Ontwerp en voorbereiding | Gearchiveerd |
| 1 | [Desktop Compleet](fase1-desktop/) | STT + LLM + Vision + Tools + TTS | ✅ Afgerond |
| 2 | [Refactor + Docker](fase2-refactor/) | Modulaire orchestrator, Docker Compose, WebSocket | ✅ Afgerond |
| 3 | [Pi Integratie](fase3-pi/) | Hardware, Camera Module 3, OLED emotie, Vision | **Actief** |
| 4 | [Autonomie](fase4-autonomie/) | Idle behaviors, SLAM, pose detectie | Gepland |

> **Nieuw:** [4-Laags Perceptie Architectuur](docs/feature-proposals/4-layer-perception-architecture.md) gepland voor Fase 3+.

> **Fase 1** omvat alles wat nodig is voor een werkende desktop demo:
> STT, LLM, Vision (via take_photo tool), Function Calling (emoties), en TTS.

## Repository Structuur

```
nerdcarx/
├── README.md                          # Dit bestand
├── ARCHITECTURE.md                    # Architectuur overzicht met C4 diagrammen
├── DECISIONS.md                       # Centrale beslissingen (bron van waarheid)
├── .gitignore                         # Git ignore regels
│
├── archive/                           # Afgeronde documenten (read-only)
│   ├── README.md                      # Uitleg archief
│   ├── 0.concept/                     # Origineel projectconcept
│   ├── old-fase-plans/                # Oude fase plannen (ter referentie)
│   ├── old-plans/                     # Gearchiveerde plannen (emotion, TTS, etc.)
│   ├── old-code/                      # Oude code (Chatterbox TTS)
│   └── old-docs/                      # Oude documentatie en research
│
├── fase1-desktop/                     # Fase 1: Desktop Compleet
│   ├── README.md                      # Overzicht en quick start
│   ├── TODO.md                        # Openstaande punten
│   ├── config.yml                     # Centrale configuratie
│   ├── stt-voxtral/                   # Speech-to-Text (Voxtral)
│   │   ├── docker/
│   │   └── README.md
│   ├── llm-ministral/                 # LLM (Ministral via Ollama)
│   ├── tts/                           # Text-to-Speech (Fish Audio)
│   │   ├── README.md
│   │   └── fishaudio/                 # Fish Audio S1-mini setup
│   ├── orchestrator/                  # FastAPI orchestrator
│   │   └── README.md
│   └── vad-desktop/                   # VAD hands-free testing
│       └── README.md
│
├── fase2-refactor/                    # Fase 2: Refactor + Docker
│   ├── README.md                      # Setup guide
│   ├── Fase2_Implementation_Plan.md   # Implementatieplan
│   ├── docker-compose.yml             # Volledige stack (Ollama + Voxtral + TTS + Orchestrator)
│   ├── config.yml                     # Centrale config
│   ├── orchestrator/                  # Modulaire FastAPI app
│   ├── stt-voxtral/                   # Voxtral Docker setup
│   ├── llm-ministral/                 # Ollama instructies
│   └── tts/fishaudio/                 # Model checkpoints + voice references
│       ├── checkpoints/               # openaudio-s1-mini model
│       └── references/                # dutch2 reference audio
│
├── fase3-pi/                          # Fase 3: Pi Integratie
│   └── Fase3_Implementation_Plan.md
│
├── fase4-autonomie/                   # Fase 4: Autonome gedragingen
│   └── Fase4_Implementation_Plan.md
│
├── docs/                              # Documentatie
│   ├── feature-proposals/             # Feature ideeën (nog niet uitgewerkt)
│   │   ├── 4-layer-perception-architecture.md
│   │   └── autonomous-room-discovery.md
│   └── hardware/                      # Hardware referentie
│       └── HARDWARE-REFERENCE.md      # Definitieve hardware configuratie
│
├── original_Picar-X-REFERENCE/        # PiCar-X documentatie (referentie)
└── original_fish-speech-REFERENCE/    # Fish Audio TTS repo + model checkpoints
```

## Quick Install

> **⚠️ Work in Progress**: Deze sectie wordt nog uitgebreid. Momenteel alleen de Docker desktop stack en Pi setup.

### Prerequisites

> **Note:** Onderstaande requirements zijn voor volledige lokale processing: STT/LLM/TTS draaien op de desktop, wake word en VAD draaien op de Pi. Cloud API's en hybrid configuraties (lagere hardware eisen) zijn gepland voor later.

**Software (Desktop):**
- Docker 24.0+ met NVIDIA Container Toolkit
- NVIDIA drivers (550+)
- Git, rsync

**Hardware (Desktop):**
- 2x GPU met voldoende VRAM (of 1 grote GPU)
  - GPU0: LLM (Ollama) + TTS → minimaal 20GB (Ministral 14B Q8 + TTS)
  - GPU1: STT (vLLM/Voxtral) → minimaal 15GB (model + KV cache)
- 32GB+ RAM

**Hardware (Pi):**
- Raspberry Pi 5 (8GB minimaal, 16GB aanbevolen)
- PiCar-X v2.0 kit (incl. USB mic, I2S speaker, Robot HAT)

---

### Desktop: Docker Stack

De stack bestaat uit 4 services in `docker-compose.yml`:

| Service | Rol | Poort |
|---------|-----|-------|
| **orchestrator** | FastAPI hub - routeert requests tussen services, WebSocket endpoint voor Pi | 8200 |
| **ollama** | LLM - Ministral 14B Q8 voor conversatie en function calling | 11434 |
| **voxtral** | STT - Speech-to-Text via vLLM met Voxtral Mini 3B | 8150 |
| **tts** | TTS - Text-to-Speech via Fish Audio S1-mini | 8250 |

#### Eerste keer: Build & Run

```bash
cd fase2-refactor

# Build images (alleen eerste keer of na code changes)
docker compose up -d --build

# Volg startup logs
docker compose logs -f
```

#### Normale startup (na eerste keer)

```bash
cd fase2-refactor
docker compose up -d

# Check status (alle 4 healthy = klaar)
docker ps --format "table {{.Names}}\t{{.Status}}"
```

#### Stoppen vs Verwijderen

```bash
# AANBEVOLEN: Stop containers (houdt state, snelle restart)
docker compose stop

# VERMIJD: Remove containers (CUDA graphs moeten opnieuw)
docker compose down  # Alleen als nodig
```

> **Belangrijk:** vLLM (Voxtral) bouwt CUDA graphs bij startup (~2 min). Stop containers liever dan ze te verwijderen voor snellere herstart.

#### Startup timing

| Service | Eerste keer | Na stop/start |
|---------|-------------|---------------|
| Ollama | ~10s | ~10s |
| TTS | ~3 min (compile) | ~30s (cached) |
| Voxtral | ~2.5 min (CUDA graphs) | ~2.5 min |
| Orchestrator | ~5s + warmup | ~5s + warmup |

- **TTS compile cache**: Na eerste run is PyTorch compile cache opgeslagen in `tts/inductor-cache/`
- **Ollama warmup**: Orchestrator laadt automatisch het LLM model in VRAM bij startup

#### Verificatie

```bash
cd fase2-refactor

# Health check
curl http://localhost:8200/health

# Chat test
curl -X POST http://localhost:8200/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hallo!"}'

# Debug logs (timing STT/LLM/TTS per turn)
docker compose logs orchestrator -f
```

---

### Pi: Client Setup

> **Voorwaarde:** Volg eerst de standaard [PiCar-X handleiding](https://docs.sunfounder.com/projects/picar-x/en/latest/) om de robot te bouwen en het Pi OS te installeren. Begin pas hierna met onderstaande NerdCarX setup.

#### 1. SSH naar Pi

```bash
ssh pi@<PI_IP_ADDRESS>
# Voorbeeld: ssh pi@192.168.1.235
```

#### 2. Conda Environment

Installeer Miniforge (aanbevolen voor ARM64):

```bash
# Download en installeer Miniforge
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
bash Miniforge3-Linux-aarch64.sh

# Herstart shell of source
source ~/.bashrc

# Maak environment
conda create -n nerdcarx python=3.13 -y
conda activate nerdcarx

# Installeer dependencies
pip install pyaudio numpy websockets openwakeword onnxruntime
```

Verificatie:
```bash
(nerdcarx) pi@nerdcarx:~ $ python --version
Python 3.13.11
```

#### 3. Sync Scripts naar Pi

Vanaf desktop:

```bash
# Sync fase3-pi folder naar Pi
rsync -avz --delete \
  ~/path/to/nerdcarx/fase3-pi/ \
  pi@<PI_IP_ADDRESS>:~/fase3-pi/

# Voorbeeld met concreet IP:
rsync -avz --delete \
  ~/vibe_claude_kilo_cli_exp/nerdcarx/fase3-pi/ \
  pi@192.168.1.235:~/fase3-pi/
```

#### 4. Run Conversation Script

Op de Pi:

```bash
conda activate nerdcarx
cd ~/fase3-pi/test_scripts

# Start conversation (wake word + voice)
python pi_conversation_v3.py
```

Het script:
1. Wacht op wake word ("hey jarvis")
2. Luistert naar spraak (VAD)
3. Stuurt audio naar desktop orchestrator
4. Speelt response audio af

> **Tip:** Debug info (timing STT/LLM/TTS) is zichtbaar in orchestrator logs:
> ```bash
> docker compose logs orchestrator -f
> ```

---

### Legacy: Fase 1 (Conda)

Zie [`fase1-desktop/README.md`](fase1-desktop/README.md) voor de oude conda-based setup zonder Docker Compose.

## Hardware Vereisten

**Desktop (AI Processing Server):**
| Component | Minimum | Aanbevolen |
|-----------|---------|------------|
| GPU | RTX 3080 (10GB) | RTX 4090 (24GB) |
| RAM | 32GB | 64GB |
| OS | Linux (Ubuntu 22.04+) | Linux |
| Docker | 24.0+ | 24.0+ |

**Robot (Pi 5 Client):**
| Component | Specificatie |
|-----------|--------------|
| Raspberry Pi 5 | 8GB RAM (16GB aanbevolen) |
| PiCar-X Kit | v2.0 |
| OLED Display | 0.96" I2C (128x64) |
| USB Microfoon | Omnidirectioneel |
| Camera | OV5647 via CSI |

## Status

**Huidige fase:** 3 - Pi Integratie

**Fase 3 - Pi Integratie:** 🔄 IN PROGRESS
- ✅ **Subfase 3a COMPLEET** - Core audio flow werkend (2026-01-17)
  - OpenWakeWord v0.4.0 (hey_jarvis) + Silero VAD v4 ONNX
  - WebSocket communicatie Pi ↔ Desktop orchestrator
  - TTS audio playback op I2S speaker
  - End-to-end test succesvol: 6 turns met function calls
- ✅ **Subfase 3a+ COMPLEET** - Remote Tool Pattern ([D016](DECISIONS.md))
  - take_photo werkt: Pi maakt foto → stuurt naar Desktop → LLM analyseert
- ✅ **Subfase 3a++ COMPLEET** - Debug & Startup optimalisatie (2026-01-17)
  - Debug logging met timing per stap (STT/LLM/Tools/TTS)
  - TTS compile cache persistent (snellere restart)
  - Ollama warmup bij startup (geen cold start failures)
  - go_to_sleep voice command (zeg "go to sleep")
  - Audio feedback: startup sound, wake word beep, sleep beeps
- ✅ **Subfase 3b COMPLEET** - OLED emotie display (2026-01-17)
  - OLED WPI438 (SSD1306) aangesloten en werkend
  - 15 emoties met geanimeerde gezichten (ogen, mond, wenkbrauwen)
  - show_emotion function calls → OLED display
  - Startup animatie, sleep gezicht
- ⏳ Camera Module 3 (verwacht 17 jan)
- Zie [`fase3-pi/Fase3_Implementation_Plan.md`](fase3-pi/Fase3_Implementation_Plan.md) voor details

**Fase 2 - Refactor + Docker:** ✅ AFGEROND (2026-01-17)
- Modulaire orchestrator met Protocol-based services
- Docker Compose stack (4 services: Ollama, Voxtral, TTS, Orchestrator)
- WebSocket endpoint werkend en getest met Pi client
- Zie [`fase2-refactor/Fase2_Implementation_Plan.md`](fase2-refactor/Fase2_Implementation_Plan.md) voor details

**Fase 1 - Desktop Compleet:** ✅ AFGEROND (2026-01-16)
- Volledige pipeline: VAD → STT → LLM → TTS → Speaker
- Function calling: `take_photo`, `show_emotion`
- Text normalisatie voor NL uitspraak (acroniemen, getallen)
- Pseudo-streaming: TTS per zin voor ~3x snellere perceived latency
- Spatiebalk interrupt tijdens audio playback
- Zie [`fase1-desktop/README.md`](fase1-desktop/README.md) voor details

**Wat werkt:**
- STT (Voxtral Mini 3B) - transcriptie via vLLM op GPU1
- LLM (Ministral 14B) - responses + function calling op GPU0
- Vision (take_photo tool) - foto analyse on-demand (remote via Pi)
- Emotion State Machine - persistente emotie state met 15 emoties
- TTS (Fish Audio S1-mini) - Nederlandse spraaksynthese + streaming
- VAD - hands-free gesprekken met gedetailleerde timing output
- Sleep mode (go_to_sleep tool) - voice command "go to sleep"
- Centrale config (config.yml)

**Hardware status:** ✅ Pi Audio Pipeline werkend (2026-01-17)
- Raspberry Pi 5 (16GB) met Pi OS Lite (Trixie, 64-bit)
- Active cooler geïnstalleerd
- Robot HAT v4 gemonteerd en werkend
- SunFounder libraries geïnstalleerd (robot-hat, vilib, picar-x)
- Motoren en servo's getest en werkend
- I2S speaker werkend (mono, GPIO 20 voor amplifier)
- Camera OV5647 werkend (wordt vervangen door Camera Module 3)
- **USB microfoon werkend met AI** (card 2, +20dB gain via software)
- **Audio pipeline Pi ↔ Desktop getest en werkend**

**Bestelde hardware (verwacht 17 jan):** ([D010](DECISIONS.md), [D012](DECISIONS.md))
- **Camera Module 3 (IMX708)**: besteld - autofocus, HDR
- **TCA9548A I2C Hub**: besteld - voor meerdere I2C devices
- **2x VL53L0X ToF sensoren**: besteld - zijwaartse afstandsmeting
- **2x Grove LED (wit)**: besteld - indicator/waarschuwingslichten
- **Grove kabels**: besteld

**Geïnstalleerd:**
- **OLED WPI438 (SSD1306)**: ✅ werkend - emotie display op I2C @ 0x3C

> **Hardware reference:** [`docs/hardware/HARDWARE-REFERENCE.md`](docs/hardware/HARDWARE-REFERENCE.md)

**TTS (Fish Audio S1-mini):**
- Model: fishaudio/openaudio-s1-mini (0.5B params)
- Nederlands via 30s ElevenLabs reference audio (dutch2)
- Pseudo-streaming: per-zin TTS via SSE
- Parameters: temp=0.5, top_p=0.6
- Service op port 8250

**Performance:**
- STT latency: 150-750ms
- LLM latency: 700-1300ms
- TTS latency: ~600ms per zin (streaming)
- Perceived latency: ~1.1s (streaming) vs ~3.6s (batch)
- Vision latency: ~5-10s (dubbele LLM call)

**Laatste update:** 2026-01-17 - Fase 3 Pi audio pipeline werkend

> **Meer weten?**
> - [`ARCHITECTURE.md`](ARCHITECTURE.md) - Uitgebreide architectuur documentatie met diagrammen
> - [`DECISIONS.md`](DECISIONS.md) - Alle beslissingen en rationale
> - [`original_Picar-X-REFERENCE/`](original_Picar-X-REFERENCE/) - PiCar-X hardware documentatie

---

*NerdCarX - Een leerproject voor AI-gestuurde robotica*
