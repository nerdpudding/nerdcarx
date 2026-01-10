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
| `FASE*-PLAN.md` | Checklist per fase | Tijdens die fase |
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
              │  STT (Voxtral/Whisper) │   WebSocket  │  Audio Capture (Mic)   │
              │  LLM (Ministral 8B)    │     LAN      │  Camera (Vision)       │
              │  TTS (Coqui/Piper)     │              │  OLED (Emoties)        │
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
| 1 | [Desktop Audio Pipeline](1.fase1-desktop-audio/) | STT → LLM → TTS, vision, function calling | **Actief** |
| 2 | [Function Calling](2.fase2-function-calling/) | OLED emoties + motor simulatie | Deels in Fase 1 |
| 3 | [Pi Integratie](3.fase3-pi-integratie/) | Hardware verbinding met Pi 5 | Wacht op hardware |
| 4 | [Vision](4.fase4-vision/) | Camera input en multimodale interactie | Deels in Fase 1 |
| 5 | [Autonomie](5.fase5-autonomie/) | Idle behaviors, proactieve interactie | Gepland |

> **Let op:** Vision en function calling zijn al basis geïmplementeerd in Fase 1.
> Later verfijnen we dit in de oorspronkelijke fases.

## Repository Structuur

```
nerdcarx/
├── README.md                          # Dit bestand
├── DECISIONS.md                       # ⭐ Centrale beslissingen (bron van waarheid)
├── .gitignore                         # Git ignore regels
│
├── archive/                           # 📁 Afgeronde documenten (read-only)
│   ├── README.md                      # Uitleg archief
│   └── 0.concept/                     # Origineel projectconcept
│       └── picar-x-ai-companion-concept.md
│
├── 1.fase1-desktop-audio/             # Fase 1: Audio pipeline
│   ├── FASE1-PLAN.md                  # Checklist en voortgang
│   └── 1a-stt-voxtral/                # Subfase 1a
│       ├── PLAN.md                    # Taken voor dit onderdeel
│       └── research/                  # Onderzoeksnotities
│
├── 2.fase2-function-calling/          # Fase 2: Function calling + emoties
│   └── FASE2-PLAN.md
│
├── 3.fase3-pi-integratie/             # Fase 3: Pi hardware
│   └── FASE3-PLAN.md
│
├── 4.fase4-vision/                    # Fase 4: Camera/Vision
│   └── FASE4-PLAN.md
│
├── 5.fase5-autonomie/                 # Fase 5: Autonome gedragingen
│   └── FASE5-PLAN.md
│
├── assets/                            # Gedeelde assets
│   └── emotions/                      # OLED emotie PNG's (128x64, 1-bit)
│
└── original_Picar-X-REFERENCE/        # PiCar-X documentatie (referentie)
```

## Quick Start

```bash
# Zie 1.fase1-desktop-audio/FASE1-PLAN.md voor complete instructies

# Kort:
# 1. Start Voxtral STT (GPU1)
cd 1.fase1-desktop-audio/1a-stt-voxtral/docker && docker compose up -d

# 2. Start Ollama LLM (GPU0)
docker run -d --gpus device=0 -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama-nerdcarx -e OLLAMA_KV_CACHE_TYPE=q8_0 ollama/ollama

# 3. Start Orchestrator
cd 1.fase1-desktop-audio/1d-orchestrator && uvicorn main:app --port 8200

# 4. Start VAD Conversation
cd 1.fase1-desktop-audio/1g-vad-desktop && python vad_conversation.py
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

**Huidige fase:** 1 - Desktop Audio Pipeline (eerste sprint)

**Wat werkt:**
- ✅ STT (Voxtral) - transcriptie
- ✅ LLM (Ministral 14B) - responses
- ✅ Vision - foto meesturen
- ✅ Function calling - emoties
- ✅ VAD - hands-free gesprekken

**Volgende stap:** TTS onderzoek

**Laatste beslissing:** [D005 - LLM keuze](DECISIONS.md) (2026-01-11)

> Zie [`DECISIONS.md`](DECISIONS.md) voor alle beslissingen en rationale.

---

*NerdCarX - Een leerproject voor AI-gestuurde robotica*
