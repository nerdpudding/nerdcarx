# Fase 3: Pi 5 Integratie

**Status:** Gepland
**Doel:** Echte hardware, services gesplitst tussen Pi en Desktop
**Afhankelijk van:** Fase 2 (Function Calling + Emoties)

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
- [ ] PiCar-X assembleren volgens handleiding
- [ ] Basis examples van SunFounder testen
- [ ] USB microfoon aansluiten en testen
- [ ] OLED display aansluiten en testen
- [ ] Camera module installeren (voor fase 4)

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

- [ ] Raspberry Pi 5 (16GB RAM aanbevolen)
- [ ] PiCar-X kit v2.0 (geassembleerd)
- [ ] USB microfoon (omnidirectioneel)
- [ ] OLED 0.96" I2C (128x64)
- [ ] Camera module (voor fase 4)
- [ ] SD card (32GB+ aanbevolen)
- [ ] Netwerk: Pi en Desktop op zelfde LAN

## Voortgang

| Datum | Update |
|-------|--------|
| - | Fase nog niet gestart |

## Notities

*Voeg hier notities, learnings en beslissingen toe tijdens de implementatie*

---

[← Fase 2](../2.fase2-function-calling/FASE2-PLAN.md) | [Terug naar README](../README.md) | [Volgende: Fase 4 →](../4.fase4-vision/FASE4-PLAN.md)
