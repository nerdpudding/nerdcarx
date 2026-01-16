# Fase 3: Pi 5 Integratie

**Status:** Hardware klaar, software wacht op fase 1 afronding
**Doel:** Echte hardware, services gesplitst tussen Pi en Desktop
**Afhankelijk van:** Fase 1 (Desktop Compleet) en Fase 2 (Refactor)

> **Nieuwe plannen:** Camera Module 3 upgrade en 4-laags perceptie architectuur.
> Zie [D010](../DECISIONS.md), [D011](../DECISIONS.md), en [4-Laags Perceptie Architectuur](../docs/feature-proposals/4-layer-perception-architecture.md).

## Overzicht

In deze fase verbinden we de Raspberry Pi 5 met de PiCar-X hardware aan de desktop server. De Pi wordt de "client" die:
- Wake word detectie doet (lokaal)
- Audio opneemt en verstuurt
- Function calls uitvoert (OLED, motors, sounds)
- Camera beelden kan versturen (voorbereiding fase 4)

## Services Verdeling

### Verhuist naar Pi
| Component | Was | Wordt | Reden |
|-----------|-----|-------|-------|
| Wake word | Desktop mock | Pi (Porcupine) | Moet altijd luisteren, lokaal |
| Audio capture | Desktop mic | Pi (USB mic) | Fysieke locatie |
| OLED control | Pygame simulator | Pi (luma.oled) | Hardware |
| Motor control | Console simulator | Pi (picar-x lib) | Hardware |
| Speaker | Desktop speaker | Pi (I2S) | Fysieke locatie |

### Mogelijk naar Pi (te evalueren)
| Component | Conditie |
|-----------|----------|
| TTS | Als Piper voldoende kwaliteit heeft en latency kritiek is |

### Blijft op Desktop
| Component | Reden |
|-----------|-------|
| Orchestrator | Centrale logica |
| STT (Voxtral) | Te zwaar voor Pi |
| LLM (Ministral) | Te zwaar voor Pi |
| TTS | Tenzij kwaliteit van Pi TTS acceptabel is |

## Taken

### Hardware Setup
- [x] PiCar-X assembleren volgens handleiding
- [x] Basis examples van SunFounder testen
- [x] USB microfoon aansluiten (AI test nog niet gedaan)
- [ ] OLED display aansluiten en testen
- [x] Camera module installeren (exposure tuning nodig)
- [ ] **Camera Module 3 installeren** (zodra besteld/ontvangen)

### Pi Client Applicatie
- [ ] Project structuur opzetten (`pi-client/`)
- [ ] Main loop: wake word → record → send → receive → execute
- [ ] WebSocket client naar desktop orchestrator
- [ ] Audio capture met VAD (Voice Activity Detection)

### Wake Word
- [ ] Picovoice Porcupine installeren
- [ ] Custom wake word "Hey robot" configureren
- [ ] Integreren in main loop
- [ ] CPU usage monitoren

### OLED Driver
- [ ] luma.oled library installeren
- [ ] show_emotion handler implementeren
- [ ] PNG assets laden en tonen
- [ ] Animatie support

### Motor Control
- [ ] picar-x library installeren
- [ ] move_robot handler implementeren
- [ ] Kalibratie van servo's
- [ ] Veiligheidslimits instellen

### Audio Output
- [ ] I2S speaker configureren
- [ ] TTS audio afspelen
- [ ] Sound effects afspelen

### Desktop Aanpassingen
- [ ] Orchestrator: WebSocket server toevoegen
- [ ] Protocol definiëren (JSON messages)
- [ ] TTS audio versturen naar Pi (of URL naar audio file)

### I2C Hardware Commissioning ([D012](../DECISIONS.md))

**Wanneer hardware binnen is:**
- [ ] I2C bus scan (`i2cdetect -y 1`) - verwacht 0x3C (OLED), 0x70 (hub)
- [ ] OLED aansluiten en testen met luma.oled
- [ ] TCA9548A hub aansluiten
- [ ] ToF sensoren via hub kanalen testen
- [ ] LEDs aansluiten op D0/D1 en testen

**ToF Sensor Integratie:**
- [ ] VL53L0X library installeren
- [ ] read_tof_left() / read_tof_right() functies
- [ ] Integratie met safety layer

**LED Indicators:**
- [ ] Obstacle warning (LEDs aan bij korte afstand)
- [ ] Status indicators (boot, error, etc.)

Zie: [Hardware Reference](../docs/hardware/HARDWARE-REFERENCE.md)

### Vision & Perceptie (4-Laags Architectuur - [D011](../DECISIONS.md))

**Laag 0: Safety (verplicht)**
- [ ] YOLO nano/small installeren op Pi
- [ ] Safety layer: obstacle detection → motor stop
- [ ] ToF sensoren integreren voor zijwaartse detectie
- [ ] Testen: robot stopt voor obstakels zonder WiFi

**Video Streaming naar Desktop**
- [ ] Streaming setup kiezen (WebRTC of MediaMTX)
- [ ] Latency meten (~200ms target)
- [ ] Desktop ontvanger voor video stream

**Laag 1: SLAM/Navigatie (optioneel, afhankelijk van timing)**
> Start wanneer Camera Module 3 binnen is. Kan ook naar Fase 4 schuiven.
- [ ] SLAM bibliotheek kiezen (ORB-SLAM3 / RTAB-Map / Stella-VSLAM)
- [ ] Basis mapping testen
- [ ] Localisatie testen

Zie ook: [4-Laags Perceptie Architectuur](../docs/feature-proposals/4-layer-perception-architecture.md)

## Architectuur

```
┌─────────────────────────────────────────────────────────────────────┐
│                              PI 5                                    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Pi Client (Python)                         │   │
│  │                                                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│  │  │ Wake Word   │  │ Audio       │  │ Function Handlers   │  │   │
│  │  │ (Porcupine) │  │ Capture     │  │ - OLED (luma.oled)  │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  │ - Motors (picar-x)  │  │   │
│  │         │                │         │ - Speaker (I2S)     │  │   │
│  │         ▼                ▼         └──────────┬──────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐           │   │
│  │  │              WebSocket Client                │           │   │
│  │  └──────────────────────┬───────────────────────┘           │   │
│  └──────────────────────────┼──────────────────────────────────┘   │
│                             │                                       │
└─────────────────────────────┼───────────────────────────────────────┘
                              │ WebSocket (LAN)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           DESKTOP                                    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  Orchestrator (FastAPI)                       │   │
│  │                                                               │   │
│  │  WebSocket Server ← → STT → LLM → TTS                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Protocol

```json
// Pi → Desktop: Audio request
{
  "type": "process",
  "audio": "<base64 encoded wav>",
  "conversation_id": "abc123",
  "state": {
    "battery_level": 85,
    "is_moving": false
  }
}

// Desktop → Pi: Response
{
  "type": "response",
  "text": "Hallo! Hoe kan ik je helpen?",
  "audio_url": "http://desktop:8000/audio/xyz.wav",
  "function_calls": [
    {"name": "show_emotion", "args": {"emotion": "happy"}}
  ]
}
```

## Pi Client Structuur

```
pi-client/
├── main.py                 # Main loop
├── audio/
│   ├── capture.py          # Mic input + VAD
│   └── playback.py         # Speaker output
├── wakeword/
│   └── porcupine.py        # Wake word handler
├── handlers/
│   ├── oled.py             # OLED emoties
│   ├── motors.py           # Motor control
│   └── sounds.py           # Sound effects
├── network/
│   └── client.py           # WebSocket client
└── config.py               # Configuratie
```

## Success Criteria

| Criterium | Test |
|-----------|------|
| Wake word werkt | "Hey robot" activeert luisteren |
| End-to-end flow | Vraag → antwoord + emotie |
| OLED werkt | show_emotion toont correcte emotie |
| Motors werken | move_robot beweegt correct |
| Audio werkt | TTS speelt af via speaker |
| Latency acceptabel | < 3 sec end-to-end |

## Hardware Checklist

### Compute & Controller
- [x] Raspberry Pi 5 (16GB RAM)
- [x] RobotHAT v4 (geïnstalleerd)
- [x] Active cooler voor Pi 5
- [x] SD card (128GB)
- [x] Netwerk: Pi en Desktop op zelfde LAN

### PiCar-X Kit (geïnstalleerd)
- [x] DC motors (2x)
- [x] Servo's (steering P2, pan P0, tilt P1)
- [x] Ultrasonic HC-SR04 (D2/D3)
- [x] Grayscale module (A0-A2)

### Camera
- [x] Camera OV5647 - werkend, wordt vervangen
- [ ] **Camera Module 3 (IMX708)** - te bestellen ([D010](../DECISIONS.md))

### I2C Devices ([D012](../DECISIONS.md))
- [ ] **OLED WPI438 (SSD1306)** - aanwezig, nog niet aangesloten
- [ ] **TCA9548A I2C Hub** - besteld
- [ ] **2x VL53L0X ToF sensoren** - besteld
- [ ] Grove kabels - besteld

### Indicators
- [ ] **2x Grove LED (wit)** - besteld (voor D0/D1)
- [ ] Grove→Dupont adapters - besteld

### Audio
- [x] I2S speaker (mono) - werkend
- [x] USB microfoon - aanwezig, nog niet getest met AI

> **Hardware reference:** [docs/hardware/HARDWARE-REFERENCE.md](../docs/hardware/HARDWARE-REFERENCE.md)

## Voortgang

| Datum | Update |
|-------|--------|
| 2026-01-14 | Hardware geassembleerd en basis tests succesvol |
| 2026-01-14 | Pi OS Lite (Trixie 64-bit) geïnstalleerd |
| 2026-01-14 | SunFounder libraries geïnstalleerd (robot-hat, vilib, picar-x) |
| 2026-01-14 | Motoren, servo's en I2S speaker getest - werkend |
| 2026-01-14 | Camera werkend maar exposure tuning nodig (donker beeld) |

## Notities

*Voeg hier notities, learnings en beslissingen toe tijdens de implementatie*

---

[← Fase 2](../2.fase2-function-calling/FASE2-PLAN.md) | [Terug naar README](../README.md) | [Volgende: Fase 4 →](../4.fase4-vision/FASE4-PLAN.md)
