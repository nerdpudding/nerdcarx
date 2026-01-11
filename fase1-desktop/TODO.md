# Plan: Fase 1 Openstaande Punten

**Datum:** 2026-01-11
**Status:** Plan voor review

---

## Overzicht

| # | Issue | Prioriteit | Status |
|---|-------|------------|--------|
| 1 | TTS klinkt soms Engelserig | Hoog | Onderzoeken |
| 2 | Prosody/expressie markers | Medium | Optioneel |
| 3 | Streaming TTS | Laag | Eerst testen |
| 4 | Playback interrupt | Laag | Spatiebalk |

**Verwijderd uit plan (niet meer van toepassing):**
- ~~VRAM memory leak~~ - Geen issue bij Fish Audio
- ~~Voxtral NL taal~~ - Al gedaan (`language: 'nl'` in vad_conversation.py:110)
- ~~Context sliding window~~ - Geen actueel probleem
- ~~Noise removal~~ - ElevenLabs audio is al clean
- ~~Korte zinnen~~ - Lengte is geen probleem voor latency

---

## 1. TTS Klinkt Soms Engelserig

### Probleem
Via orchestrator klinkt TTS soms met Engels accent, terwijl standalone tests goed klinken.

### Huidige config check
System prompt bevat: "Je antwoordt in het Nederlands, natuurlijk en behulpzaam"

Maar bevat NIET expliciet: "Vermijd Engelse termen"

### Mogelijke oorzaak
LLM gebruikt soms Engelse woorden/zinstructuren die TTS beïnvloeden.

### Aanbevolen actie

**Optie A: Prompt toevoegen** (5 min)
```yaml
# config.yml - toevoegen aan system_prompt
Gebruik bij voorkeur Nederlandse woorden. Vermijd onnodige Engelse termen.
```

**Optie B: Langere reference audio** (30 min testen)
- Huidige: `reference2_NL_FM.mp3` (kort)
- Nieuw: 15-20s opname met diverse Nederlandse zinnen
- **Let op:** Test of dit latency beïnvloedt!

**Optie C: Fine-tuning** (voor later, 2-4 uur)
- ~30 min NL audio met transcripties
- Training: 1-2 uur op RTX 4090
- Overwegen als A en B niet voldoende helpen

---

## 2. Prosody/Expressie Markers (optioneel)

### Analyse
Perplexity beweert dat emotie markers niet werken voor Nederlands. Maar:
- `(happy)`, `(sad)`, `(excited)` → **Werken NIET voor NL**
- `(laughing)`, `(whispering)`, `(sighing)`, `(chuckling)` → **Taal-agnostisch, kunnen werken**

### Implementatie (indien gewenst)
```python
# orchestrator/main.py - synthesize_speech()
EMOTION_PROSODY = {
    "happy": "(chuckling)",
    "excited": "(laughing)",
    "shy": "(whispering)",
    "sad": "(sighing)",
}

prosody = EMOTION_PROSODY.get(emotion, "")
text = f"{prosody} {text}" if prosody else text
```

### Aanbeveling
Test eerst of deze markers überhaupt effect hebben op de output voordat we dit implementeren.

---

## 3. Streaming TTS (optioneel)

### Achtergrond
Eerdere poging met streaming gaf **ruis**. Wat is er nu anders?

### API ondersteunt streaming
Fish Audio API (`views.py:147-162`) ondersteunt `streaming: true` parameter.

### Waarom eerder ruis?
Perplexity noemt: chunks moeten met **10ms padding** aan elkaar geplakt worden om klikken/ruis te voorkomen.

```python
# Padding tussen chunks
padding = np.zeros(int(24000 * 0.01), dtype=np.float32)  # 10ms @ 24kHz
```

### Aanbevolen aanpak

**Stap 1: Test BUITEN orchestrator** (standalone script)
```python
# test_streaming.py
import httpx
import numpy as np

response = httpx.post(
    "http://localhost:8250/v1/tts",
    json={
        "text": "Dit is een test zin voor streaming.",
        "reference_id": "dutch2",
        "streaming": True,
        "format": "wav"
    },
    stream=True
)

chunks = []
for chunk in response.iter_bytes():
    chunks.append(chunk)
    # Voeg padding toe tussen chunks

# Test of audio zonder ruis is
```

**Stap 2: Als test succesvol** → integreer in orchestrator

### Huidige situatie
~1.2s latency is **acceptabel**. Streaming is nice-to-have, niet kritiek.

---

## 4. Playback Interrupt

### Oplossing: Spatiebalk (desktop)

```python
# vad_conversation.py - play_audio()
import threading

stop_event = threading.Event()

def keyboard_listener():
    import keyboard
    keyboard.wait('space')
    stop_event.set()

thread = threading.Thread(target=keyboard_listener, daemon=True)
thread.start()

# In playback loop: check stop_event.is_set()
```

### Later (hardware)
Als Pi hardware komt, andere oplossing nodig (wake word, button, etc.). Daar later over nadenken.

---

## Volgorde van Aanpak

| # | Actie | Tijd | Prioriteit |
|---|-------|------|------------|
| 1 | Prompt aanpassen (Engelse termen) | 5 min | Proberen |
| 2 | Test langere reference audio | 30 min | Optioneel |
| 3 | Test streaming buiten orchestrator | 30 min | Optioneel |
| 4 | Spatiebalk interrupt | 30 min | Nice-to-have |

**Totaal als alles:** ~1.5 uur

---

## Bestanden

| Wijziging | Bestand |
|-----------|---------|
| Prompt Engelse termen | `config.yml` |
| Reference audio | `tts/fishaudio/elevenreference/` |
| Prosody markers | `orchestrator/main.py` |
| Streaming test | Nieuw: `tts/test_streaming.py` |
| Playback interrupt | `vad-desktop/vad_conversation.py` |

---

## Verificatie

Na wijzigingen:
1. Start conversatie
2. Luister of TTS Nederlandser klinkt
3. Test expressie (als prosody geïmplementeerd)
4. Test spatiebalk interrupt (als geïmplementeerd)
