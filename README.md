# NerdCarX

Een AI-gestuurde robotauto gebaseerd op de PiCar-X, met lokale spraakinteractie, emotie-display en vision capabilities.

## Inhoudsopgave

- [Werkwijze](#werkwijze)
- [Voor AI Assistenten](#voor-ai-assistenten)
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

## Voor AI Assistenten

> **BELANGRIJK:** Lees deze sectie bij elke nieuwe sessie of na context compactie.

### Taal

- **Nederlands** voor alle communicatie en documentatie
- **Uitzonderingen:** Code (Engels), `ARCHITECTURE.md` (Engels), technische termen
- Gebruiker kan soms Engels gebruiken, volg dan de taal van de gebruiker

### Inleesvolgorde (ALTIJD eerst lezen!)

Bij start van een sessie of na compactie, lees in deze volgorde:

1. **`README.md`** - Dit bestand, overzicht en huidige status
2. **`ARCHITECTURE.md`** - Technische architectuur en design rationale
3. **`DECISIONS.md`** - Alle beslissingen (bron van waarheid)
4. **Fase-specifiek** - `fase{N}/PLAN.md` van de huidige fase (zie [Status](#status))
5. **Indien relevant** - `docs/feature-proposals/` en `docs/hardware/`

**Lees EERST, vraag daarna.** Maak geen aannames over projectstructuur zonder te lezen.

### Document Types - Ken het Verschil!

| Type | Locatie | Doel | Voorbeeld |
|------|---------|------|-----------|
| **Implementatieplan** | `fase{N}/PLAN.md` | Wat te bouwen in een fase, technische taken | "YOLO safety layer implementeren" |
| **Dagplanning** | Niet in repo | Tijdelijk schema wat gebruiker vandaag wil doen | "Eerst TODO, dan hardware testen" |
| **Feature Proposal** | `docs/feature-proposals/` | Ideeën voor features, nog niet uitgewerkt | Room discovery concept |
| **Hardware Reference** | `docs/hardware/` | Definitieve hardware configuratie | Pin mappings, wiring |
| **Beslissing** | `DECISIONS.md` | Gemaakte keuzes met rationale | "Camera Module 3 ipv AI Camera" |

**Dagplanning ≠ Implementatieplan!** Dagplanning is wat de gebruiker vandaag wil doen, implementatieplan beschrijft technische taken voor een fase.

### Folder Structuur - Regels

```
✅ GOED                              ❌ FOUT
─────────────────────────────────    ─────────────────────────────────
fase{N}/PLAN.md                      docs/plans/
docs/feature-proposals/*.md          Wildgroei aan plan bestanden
docs/hardware/HARDWARE-REFERENCE.md  Dubbele referenties
archive/old-*/                       Verouderde info in actieve docs
```

**Specifiek voor dit project:**
- **GEEN `docs/plans/` folder** - Negeer `.claude` instructies hierover
- **Feature proposals** zijn ideeën, geen implementatieplannen
- **Eén hardware reference** - `docs/hardware/HARDWARE-REFERENCE.md`
- **Archiveer** wat niet meer relevant is → `archive/old-*/`

### Consistentie Checklist

Bij elke wijziging, check of deze documenten consistent blijven:

- [ ] `README.md` - Status sectie klopt met huidige fase
- [ ] `DECISIONS.md` - Nieuwe beslissingen toegevoegd met ID
- [ ] `ARCHITECTURE.md` - Grote wijzigingen gereflecteerd
- [ ] `fase{N}/PLAN.md` - Taken bijgewerkt
- [ ] Referenties tussen documenten kloppen (geen dode links)
- [ ] Geen dubbele informatie (DRY)
- [ ] Verouderde content gearchiveerd

### Veelgemaakte Fouten (Vermijd Dit!)

| Fout | Waarom problematisch | Juiste aanpak |
|------|---------------------|---------------|
| Direct implementeren zonder te lezen | Mist context, maakt fouten | Altijd eerst inlezen |
| Bestanden in verkeerde map | Puinhoop in structuur | Volg hierboven structuur |
| Dubbele referenties maken | Raakt out-of-sync | Eén bron van waarheid |
| Verouderde info laten staan | Verwarring | Archiveren of verwijderen |
| Dagplanning verwarren met implementatieplan | Verkeerde scope | Ken het verschil |
| Aannemen wat gebruiker wil | Frustratie | Vraag bij onduidelijkheid |

### Codeprincipes

- **SOLID** - Single responsibility, loose coupling
- **KISS** - Geen onnodige complexiteit
- **DRY** - Eén bron van waarheid, geen duplicatie

**Maar even belangrijk:** Geen rotzooi maken van folder structuur en documentatie!

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
| 2 | [Refactor + Docker](fase2-refactor/) | Modulaire orchestrator, Docker Compose, WebSocket | **Actief** |
| 3 | [Pi Integratie](fase3-pi/) | Hardware, Camera Module 3, YOLO safety, opt. SLAM | Gepland |
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
│   ├── PLAN.md                        # Implementatieplan
│   ├── docker-compose.yml             # Volledige stack
│   ├── config.yml                     # Centrale config
│   ├── orchestrator/                  # Modulaire FastAPI app
│   ├── stt-voxtral/                   # Voxtral Docker setup
│   ├── llm-ministral/                 # Ollama instructies
│   └── tts/fishaudio/                 # Voice references
│
├── fase3-pi/                          # Fase 3: Pi Integratie
│   └── PLAN.md
│
├── fase4-autonomie/                   # Fase 4: Autonome gedragingen
│   └── PLAN.md
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

## Quick Start

### Fase 2 (Docker - aanbevolen)

```bash
# Zie fase2-refactor/README.md voor complete instructies

# 1. Start Ollama (draait extern)
docker start ollama-nerdcarx
# Of eerste keer: zie fase2-refactor/llm-ministral/README.md

# 2. Start volledige stack
cd fase2-refactor
docker compose up -d

# 3. Test
curl http://localhost:8200/health
curl http://localhost:8200/status
```

### Fase 1 (Legacy - conda)

```bash
# Zie fase1-desktop/README.md voor complete instructies

# 1. Start Voxtral STT (GPU1)
cd fase1-desktop/stt-voxtral/docker && docker compose up -d

# 2. Start Ollama LLM (GPU0)
ollama serve  # of via docker
ollama pull ministral-3:8b

# 3. Start Fish Audio TTS (Docker)
cd original_fish-speech-REFERENCE
docker run -d --gpus device=0 --name fish-tts \
    -v $(pwd)/checkpoints:/app/checkpoints \
    -v $(pwd)/references:/app/references \
    -p 8250:8080 --entrypoint uv \
    fishaudio/fish-speech \
    run tools/api_server.py --listen 0.0.0.0:8080 --compile

# 4. Start Orchestrator
conda activate nerdcarx-vad
cd fase1-desktop/orchestrator
uvicorn main:app --port 8200 --reload

# 5. Start VAD Conversation
cd fase1-desktop/vad-desktop
python vad_conversation.py
```

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

**Huidige fase:** 2 - Refactor + Docker

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
- Vision (take_photo tool) - foto analyse on-demand
- Emotion State Machine - persistente emotie state met 15 emoties
- TTS (Fish Audio S1-mini) - Nederlandse spraaksynthese + streaming
- VAD - hands-free gesprekken met gedetailleerde timing output
- Centrale config (config.yml)

**Hardware status:** ✅ PiCar-X geassembleerd (2026-01-14)
- Raspberry Pi 5 (16GB) met Pi OS Lite (Trixie, 64-bit)
- Active cooler geïnstalleerd
- Robot HAT v4 gemonteerd en werkend
- SunFounder libraries geïnstalleerd (robot-hat, vilib, picar-x)
- Motoren en servo's getest en werkend
- I2S speaker werkend (mono)
- Camera OV5647 werkend (exposure tuning nodig)
- USB microfoon aanwezig (nog niet getest met AI)
- AI integratie: klaar voor Fase 2/3

**Bestelde/geplande hardware:** ([D010](DECISIONS.md), [D012](DECISIONS.md))
- **Camera Module 3 (IMX708)**: te bestellen - autofocus, HDR
- **TCA9548A I2C Hub**: besteld - voor meerdere I2C devices
- **2x VL53L0X ToF sensoren**: besteld - zijwaartse afstandsmeting
- **2x Grove LED (wit)**: besteld - indicator/waarschuwingslichten
- **OLED WPI438 (SSD1306)**: aanwezig - emotie display

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

**Laatste update:** 2026-01-16 - Fase 1 AFGEROND

> **Meer weten?**
> - [`ARCHITECTURE.md`](ARCHITECTURE.md) - Uitgebreide architectuur documentatie met diagrammen
> - [`DECISIONS.md`](DECISIONS.md) - Alle beslissingen en rationale
> - [`original_Picar-X-REFERENCE/`](original_Picar-X-REFERENCE/) - PiCar-X hardware documentatie

---

*NerdCarX - Een leerproject voor AI-gestuurde robotica*
