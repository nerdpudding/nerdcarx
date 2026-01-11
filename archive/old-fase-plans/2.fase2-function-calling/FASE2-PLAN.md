# Fase 2: Function Calling + Emoties

**Status:** Gepland
**Doel:** LLM triggert acties via function calls, getest met desktop simulators
**Afhankelijk van:** Fase 1 (Audio Pipeline)

## Overzicht

In deze fase voegen we function calling toe aan de LLM en bouwen we desktop simulators om de Pi hardware te simuleren:
- OLED display → Pygame window
- Motors/Servo's → Console output of animatie
- Geluidseffecten → Desktop audio

## Taken

### Function Calling Schema
- [ ] Tools schema definiëren (show_emotion, move_robot, play_sound, etc.)
- [ ] Schema toevoegen aan Ministral system prompt
- [ ] Function call parsing in orchestrator

### OLED Simulator
- [ ] Pygame window opzetten (128x64 schaal)
- [ ] Emotie PNG assets laden (1-bit zwart/wit)
- [ ] show_emotion handler implementeren
- [ ] Animatie support (blink, transitions)

### Motor Simulator
- [ ] move_robot handler implementeren
- [ ] Console output of visuele feedback
- [ ] Bewegingstypen: forward, backward, turn_left, turn_right, etc.

### Sound Player
- [ ] play_sound handler implementeren
- [ ] Basis geluidseffecten verzamelen/maken
- [ ] Desktop audio playback

### Integratie
- [ ] Orchestrator routeert function calls naar simulators
- [ ] Meerdere function calls in één response
- [ ] Function calls parallel met TTS response

### Assets
- [ ] OLED emotie PNG's maken (128x64, 1-bit)
  - [ ] happy, sad, thinking, surprised, angry
  - [ ] love, confused, sleeping, excited, neutral
  - [ ] listening (voor na wake word)
- [ ] Geluidseffecten verzamelen

## Architectuur

```
desktop-mockup/
├── oled_simulator.py      # Pygame window 128x64
├── motor_simulator.py     # Console/visuele beweging output
├── sound_player.py        # Desktop audio voor effecten
└── main.py                # Start alle simulators
```

```
Orchestrator Flow:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  LLM Response: {                                            │
│    text: "Gefeliciteerd!",                                  │
│    function_calls: [                                        │
│      {name: "show_emotion", args: {emotion: "happy"}}       │
│    ]                                                        │
│  }                                                          │
│                                                             │
│            ┌────────────────┬────────────────┐              │
│            ▼                ▼                ▼              │
│     ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│     │   TTS    │    │   OLED   │    │  Motors  │           │
│     │ (audio)  │    │(emotie)  │    │(beweging)│           │
│     └──────────┘    └──────────┘    └──────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Function Calling Schema

```json
{
  "tools": [
    {
      "name": "show_emotion",
      "parameters": {
        "emotion": ["happy", "sad", "thinking", "surprised", "angry",
                    "love", "confused", "sleeping", "excited", "neutral"],
        "intensity": ["subtle", "normal", "exaggerated"]
      }
    },
    {
      "name": "move_robot",
      "parameters": {
        "action": ["forward", "backward", "turn_left", "turn_right",
                   "spin", "nod_yes", "shake_no", "look_around", "dance", "stop"],
        "speed": 1-100,
        "duration_ms": 100-5000
      }
    },
    {
      "name": "play_sound",
      "parameters": {
        "sound": ["beep", "happy_tune", "sad_tune", "alert",
                  "greeting", "goodbye", "thinking", "error"]
      }
    }
  ]
}
```

## Success Criteria

| Criterium | Test |
|-----------|------|
| show_emotion werkt | "Dankjewel!" → OLED toont happy |
| Sentiment detectie | "Ik ben verdrietig" → sad emotie |
| move_robot werkt | "Draai rond" → simulator toont beweging |
| Meerdere calls | Response met tekst + emotie + beweging |
| play_sound werkt | Geluidseffecten spelen af |

## Test Scenarios

```
Input: "Dankjewel, dat maakte me blij!"
Expected:
  - TTS: sympathiek antwoord
  - OLED: happy emotie
  - Sound: happy_tune (optioneel)

Input: "Ik heb slecht nieuws gekregen"
Expected:
  - TTS: meelevend antwoord
  - OLED: sad of concerned emotie

Input: "Draai 90 graden naar links"
Expected:
  - TTS: "Begrepen" of bevestiging
  - Motor: turn_left actie in simulator
  - OLED: focused emotie
```

## Voortgang

| Datum | Update |
|-------|--------|
| - | Fase nog niet gestart |

## Notities

*Voeg hier notities, learnings en beslissingen toe tijdens de implementatie*

---

[← Fase 1](../1.fase1-desktop-audio/FASE1-PLAN.md) | [Terug naar README](../README.md) | [Volgende: Fase 3 →](../3.fase3-pi-integratie/FASE3-PLAN.md)
