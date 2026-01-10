# NerdCarX

Een AI-gestuurde robotauto gebaseerd op de PiCar-X, met lokale spraakinteractie, emotie-display en vision capabilities.

## Inhoudsopgave

- [Doelstelling](#doelstelling)
- [Concept Samenvatting](#concept-samenvatting)
- [Fasen](#fasen)
- [Repository Structuur](#repository-structuur)
- [Quick Start](#quick-start)
- [Hardware Vereisten](#hardware-vereisten)
- [Status](#status)

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
| 0 | [Concept](0.nerdcarx-concept/) | Ontwerp en voorbereiding | Actief |
| 1 | [Desktop Audio Pipeline](1.fase1-desktop-audio/) | STT → LLM → TTS volledig in Docker | Gepland |
| 2 | [Function Calling](2.fase2-function-calling/) | OLED emoties + motor simulatie | Gepland |
| 3 | [Pi Integratie](3.fase3-pi-integratie/) | Hardware verbinding met Pi 5 | Gepland |
| 4 | [Vision](4.fase4-vision/) | Camera input en multimodale interactie | Gepland |
| 5 | [Autonomie](5.fase5-autonomie/) | Idle behaviors, proactieve interactie | Gepland |

## Repository Structuur

```
nerdcarx/
├── README.md                          # Dit bestand
├── .gitignore                         # Git ignore regels
│
├── 0.nerdcarx-concept/                # Concept documentatie
│   └── picar-x-ai-companion-concept.md
│
├── 1.fase1-desktop-audio/             # Fase 1: Audio pipeline
│   ├── FASE1-PLAN.md                  # Plan en voortgang
│   └── services/                      # Docker services (komt later)
│
├── 2.fase2-function-calling/          # Fase 2: Function calling + emoties
│   ├── FASE2-PLAN.md                  # Plan en voortgang
│   └── desktop-mockup/                # Simulators (komt later)
│
├── 3.fase3-pi-integratie/             # Fase 3: Pi hardware
│   ├── FASE3-PLAN.md                  # Plan en voortgang
│   └── pi-client/                     # Pi applicatie (komt later)
│
├── 4.fase4-vision/                    # Fase 4: Camera/Vision
│   ├── FASE4-PLAN.md                  # Plan en voortgang
│   └── ...
│
├── 5.fase5-autonomie/                 # Fase 5: Autonome gedragingen
│   ├── FASE5-PLAN.md                  # Plan en voortgang
│   └── ...
│
├── assets/                            # Gedeelde assets
│   └── emotions/                      # OLED emotie PNG's (128x64, 1-bit)
│
└── original_Picar-X-REFERENCE/        # Originele PiCar-X documentatie (referentie)
    └── Documentation/
        └── manual-chapters/
```

## Quick Start

> Het project is nog in conceptfase. Quick start instructies volgen zodra fase 1 gereed is.

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

**Huidige fase:** 0 - Concept

**Voortgang:**
- [x] Concept document geschreven
- [ ] README en project structuur
- [ ] Fase documenten aangemaakt
- [ ] .gitignore toegevoegd
- [ ] Git repository geinitialiseerd

---

*NerdCarX - Een leerproject voor AI-gestuurde robotica*
