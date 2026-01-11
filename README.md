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
| `DECISIONS.md` | Alle beslissingen | Bij elke keuze |
| `README.md` | Overzicht + huidige fase | Bij fasewissel |
| `archive/` | Afgeronde documenten (read-only) | Nooit |
| `*/PLAN.md` | Checklist per fase | Tijdens die fase |
| `research/` | Losse notities | Vrij |

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
              │  TTS (Chatterbox)      │              │  OLED (Emoties)        │
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
| 1 | [Desktop Compleet](fase1-desktop/) | STT + LLM + Vision + Tools + TTS | **Actief** |
| 2 | [Refactor + Docker](fase2-refactor/) | Code cleanup, dockerizen, SOLID/KISS | Gepland |
| 3 | [Pi Integratie](fase3-pi/) | Hardware verbinding met Pi 5 | Wacht op hardware |
| 4 | [Autonomie](fase4-autonomie/) | Idle behaviors, proactieve interactie | Gepland |

> **Fase 1** omvat alles wat nodig is voor een werkende desktop demo:
> STT, LLM, Vision (via take_photo tool), Function Calling (emoties), en TTS.

## Repository Structuur

```
nerdcarx/
├── README.md                          # Dit bestand
├── DECISIONS.md                       # Centrale beslissingen (bron van waarheid)
├── .gitignore                         # Git ignore regels
│
├── archive/                           # Afgeronde documenten (read-only)
│   ├── README.md                      # Uitleg archief
│   ├── 0.concept/                     # Origineel projectconcept
│   ├── old-fase-plans/                # Oude fase plannen (ter referentie)
│   └── old-plans/                     # Gearchiveerde plannen (emotion, TTS, etc.)
│
├── fase1-desktop/                     # Fase 1: Desktop Compleet
│   ├── PLAN.md                        # Checklist en voortgang
│   ├── TESTPLAN.md                    # Test handleiding
│   ├── config.yml                     # Centrale configuratie
│   ├── stt-voxtral/                   # Speech-to-Text (Voxtral)
│   │   ├── docker/
│   │   └── README.md
│   ├── llm-ministral/                 # LLM (Ministral via Ollama)
│   │   └── README.md
│   ├── tts/                           # Text-to-Speech (Chatterbox)
│   │   ├── README.md
│   │   ├── tts_service.py             # FastAPI TTS service
│   │   └── test_chatterbox.py         # Test script
│   ├── orchestrator/                  # FastAPI orchestrator
│   │   └── README.md
│   └── vad-desktop/                   # VAD hands-free testing
│       └── README.md
│
├── fase2-refactor/                    # Fase 2: Refactor + Docker
│   └── PLAN.md
│
├── fase3-pi/                          # Fase 3: Pi Integratie
│   └── PLAN.md
│
├── fase4-autonomie/                   # Fase 4: Autonome gedragingen
│   └── PLAN.md
│
├── original_Picar-X-REFERENCE/        # PiCar-X documentatie (referentie)
└── original_chatterbox-REFERENCE/     # Chatterbox TTS repo (referentie)
```

## Quick Start

```bash
# Zie fase1-desktop/PLAN.md voor complete instructies

# 1. Start Voxtral STT (GPU1)
cd fase1-desktop/stt-voxtral/docker && docker compose up -d

# 2. Start Ollama LLM (GPU0)
ollama serve  # of via docker
ollama pull ministral-3:8b

# 3. Start TTS Service (aparte conda env!)
conda activate nerdcarx-tts
cd fase1-desktop/tts
uvicorn tts_service:app --port 8250

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

**Huidige fase:** 1 - Desktop Compleet

**Wat werkt:** ✅ Alle onderdelen geïmplementeerd (2026-01-11)
- STT (Voxtral) - transcriptie via vLLM op GPU1
- LLM (Ministral 8B/14B) - responses + function calling op GPU0
- Vision (take_photo tool) - foto analyse on-demand
- Emotion State Machine - persistente emotie state met 15 emoties
- TTS (Chatterbox) - Nederlandse spraaksynthese met emotie
- VAD - hands-free gesprekken met duidelijke debug output
- Centrale config (config.yml) met hot reload

**TTS (Chatterbox Multilingual):**
- Model: ResembleAI/chatterbox (500M params)
- Nederlands native support
- Emotie → exaggeration parameter mapping
- Aparte conda env: `nerdcarx-tts`
- Service op port 8250

**Performance:**
- Vision latency: ~5-10s (acceptabel voor demo)
- TTS latency: ~1-2s per zin
- Emotion response: instant (tool call parsing)

**Volgende stap:** End-to-end testing, daarna Fase 2 (Refactor)

**Laatste beslissing:** [D008 - TTS Chatterbox](DECISIONS.md) (2026-01-11)

> Zie [`DECISIONS.md`](DECISIONS.md) voor alle beslissingen en rationale.

---

*NerdCarX - Een leerproject voor AI-gestuurde robotica*
