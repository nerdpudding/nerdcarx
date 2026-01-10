# Subfase 1g: VAD - Desktop Testing

**Status:** Gepland
**Doel:** Voice Activity Detection voor hands-free testing van de audio pipeline op desktop

---

## Context

VAD (Voice Activity Detection) detecteert wanneer iemand begint en stopt met spreken. Dit maakt hands-free testing mogelijk: spreek gewoon, en het systeem stuurt automatisch naar Voxtral wanneer je klaar bent.

**Let op:** Dit is een **desktop testing tool**. De VAD oplossing voor de Pi wordt later apart onderzocht - die kan anders zijn (Picovoice Cobra, andere library, of wellicht toch Silero).

---

## Doel

Een simpele VAD setup die:
1. Luistert naar de microfoon
2. Detecteert wanneer spraak begint
3. Neemt op totdat stilte wordt gedetecteerd
4. Stuurt audio naar Voxtral (localhost:8150)
5. Print/retourneert het resultaat

---

## Onderzoeksvragen

### VAD Library

| Vraag | Te Onderzoeken |
|-------|----------------|
| Silero VAD geschikt? | Lightweight, accuraat, MIT license |
| Alternatieven? | webrtcvad, Picovoice Cobra (voor later vergelijk) |
| Sample rate? | 16kHz vereist voor Silero |
| Chunk size? | 30ms chunks aanbevolen |

### Integratie

| Vraag | Te Onderzoeken |
|-------|----------------|
| PyAudio vs sounddevice? | Welke werkt beter met onze mic |
| Silence timeout? | Hoeveel stilte = einde spraak |
| Feedback? | Visuele/audio feedback tijdens opname |

### Performance

| Vraag | Te Onderzoeken |
|-------|----------------|
| CPU gebruik | Silero claimt ~0.4% CPU |
| Latency | Detectie snelheid |
| False positives | Achtergrondgeluid handling |

---

## Environment Setup

Conda alleen voor Python environment, alle packages via pip.

```bash
# Maak conda environment met Python 3.14 (laatste stable)
conda create -n nerdcarx-vad python=3.14 -y
conda activate nerdcarx-vad

# Installeer dependencies via pip
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install silero-vad pyaudio requests
```

**Dependencies:**
| Package | Versie | Doel |
|---------|--------|------|
| torch | latest | Backend voor Silero |
| torchaudio | latest | Audio processing |
| silero-vad | latest | Voice Activity Detection |
| pyaudio | latest | Microfoon input |
| requests | latest | HTTP naar Voxtral |

---

## Implementatieplan

### Stap 1: Environment Setup

- [ ] Conda environment aanmaken (Python 3.14)
- [ ] Dependencies installeren via pip
- [ ] Microfoon testen

### Stap 2: Basis VAD Script

- [ ] Microfoon selectie
- [ ] Silero VAD laden
- [ ] Audio stream starten
- [ ] Spraak detectie implementeren

### Stap 3: Voxtral Integratie

- [ ] Audio naar Voxtral sturen na detectie
- [ ] Transcriptie teruggeven
- [ ] Optioneel: chat mode (antwoord direct)

### Stap 4: Polish

- [ ] Silence timeout configureerbaar
- [ ] Visuele feedback (emoji status)
- [ ] Error handling

---

## Technische Details

### Silero VAD

- **Model size:** 1.8MB
- **Speed:** ~1ms per 30ms chunk
- **Sample rate:** 8kHz of 16kHz
- **Threshold:** >0.5 = spraak gedetecteerd
- **License:** MIT

### Audio Flow

```
[Microfoon] → [PyAudio 16kHz] → [Silero VAD] → [Buffer]
                                     │
                                     ▼
                              Spraak gedetecteerd?
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                       Ja                        Nee
                        │                         │
                   Start opname              Wacht verder
                        │
                        ▼
                 [Buffer vullen]
                        │
                        ▼
                 Stilte gedetecteerd?
                        │
                       Ja
                        │
                        ▼
              [Stuur naar Voxtral]
                        │
                        ▼
                 [Print resultaat]
```

### Configuratie

| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `SAMPLE_RATE` | 16000 | Sample rate (Hz) |
| `CHUNK_SIZE` | 512 | Samples per chunk (~32ms @ 16kHz) |
| `SILENCE_THRESHOLD` | 0.5 | VAD threshold |
| `SILENCE_DURATION` | 1.5s | Stilte voor einde detectie |
| `MIN_SPEECH_DURATION` | 0.3s | Minimale spraak duur |

---

## Gebruik (Gepland)

```bash
# Activeer environment
conda activate nerdcarx-vad

# Start VAD listener (transcriptie mode)
python vad_listen.py

# Chat mode (Voxtral beantwoordt direct)
python vad_listen.py --chat

# Custom silence timeout
python vad_listen.py --silence-duration 2.0
```

**Verwachte output:**
```
🎤 VAD Listener gestart
🎧 Luisteren... (spreek wanneer klaar)

🔴 Spraak gedetecteerd - opname gestart
⏸️ Stilte gedetecteerd - opname gestopt
📤 Audio verzenden naar Voxtral...
📝 Transcriptie: "Wat is de hoofdstad van Frankrijk?"

🎧 Luisteren... (spreek wanneer klaar)
```

---

## Nu vs Later

### Nu: Desktop Testing (Simpel)

- **Alleen VAD** - geen wake word
- Altijd luisteren, detecteer spraak, stuur naar Voxtral
- Doel: snel de audio pipeline kunnen testen

### Later: Pi Implementatie (Nog te Bepalen)

**Conversatie Flow - Nog uit te werken:**

```
┌─────────────────────────────────────────────────────────┐
│  IDLE: Wacht op wake word ("Hey robot")                 │
│  - Alleen wake word detection actief (zuinig)           │
└────────────────────┬────────────────────────────────────┘
                     │ Wake word gedetecteerd
                     ▼
┌─────────────────────────────────────────────────────────┐
│  CONVERSATION MODE                                      │
│  - VAD actief (geen wake word nodig per turn)           │
│  - Natuurlijk heen-en-weer praten                       │
│  - Robot antwoordt, luistert dan voor volgende vraag    │
│                                                         │
│  Terug naar IDLE na:                                    │
│  - X seconden stilte (timeout)                          │
│  - Gebruiker zegt "doei" / "bedankt" / etc.            │
│  - Expliciet commando                                   │
└─────────────────────────────────────────────────────────┘
```

**Open beslissingen voor Pi:**

| Vraag | Opties | Te bepalen |
|-------|--------|------------|
| Wake word library? | Porcupine, OpenWakeWord, andere | Performance vs licentie |
| VAD library? | Silero, Cobra, webrtcvad, andere | Accuraatheid vs resources |
| Conversation timeout? | 5s, 10s, 30s? | Testen wat natuurlijk voelt |
| Hoe terug naar IDLE? | Timeout, keyword, beide? | UX testen |
| Wake word customization? | "Hey robot", "Hallo NerdCarX"? | Accuraatheid testen |
| Streaming? | VAD→STT→LLM→TTS streaming | Latency vs complexiteit |

**VAD opties voor Pi:**

| Optie | Pro | Con |
|-------|-----|-----|
| **Silero VAD** | Lightweight, werkt op Pi, bekend | Python overhead |
| **Picovoice Cobra** | Geoptimaliseerd voor edge | Closed source |
| **webrtcvad** | Zeer licht, C-based | Minder accuraat |

**Wake word opties voor Pi:**

| Optie | Pro | Con |
|-------|-----|-----|
| **Porcupine** | Accuraat, custom wake words, gratis hobby | Closed source |
| **OpenWakeWord** | Open source, trainbaar | Minder accuraat |
| **Vosk** | Open source, offline | Meer resources |

De keuze hangt af van:
- Performance requirements op Pi 5
- Gewenste wake word(s)
- Resource budget (CPU/RAM)
- Licentie overwegingen

---

## Resources

- [Silero VAD GitHub](https://github.com/snakers4/silero-vad)
- [PyAudio Streaming Examples](https://github.com/snakers4/silero-vad/tree/master/examples/pyaudio-streaming)
- [Python 3.14 Release](https://www.python.org/downloads/release/python-3140/)
- [Picovoice Cobra](https://picovoice.ai/platform/cobra/) (voor later vergelijk)

---

[← Terug naar Fase 1](../FASE1-PLAN.md)
