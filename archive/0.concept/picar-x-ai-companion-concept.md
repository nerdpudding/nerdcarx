# PiCar-X AI Companion - Project Concept

> **⚠️ STATUS: CONCEPT DOCUMENT**
>
> Dit document beschrijft een **conceptueel ontwerp** dat nog in ontwikkeling is.
> - Alle keuzes zijn **voorlopig** en kunnen wijzigen op basis van experimenten
> - Technische specificaties zijn **schattingen**, niet gemeten waarden
> - Architectuur en tooling worden **iteratief** bepaald tijdens ontwikkeling
> - Dit is een leer- en hobbyproject zonder vaste einddatum
>
> Niets in dit document is definitief totdat het geïmplementeerd en getest is.

---

## Inhoudsopgave

1. [Vision](#vision)
2. [Uitgangspunten](#uitgangspunten)
3. [Use Cases](#use-cases)
4. [Robot State & Situational Awareness](#robot-state--situational-awareness)
5. [Aanpak](#aanpak)
6. [Hardware Setup](#hardware-setup)
7. [Model Rollen](#model-rollen---verduidelijkt)
8. [Architectuur](#architectuur)
9. [Wake Word Opties](#wake-word-opties-pi-lokaal)
10. [TTS Opties](#tts-opties)
11. [Function Calling Schema](#function-calling-schema)
12. [OLED Emotie Systeem](#oled-emotie-systeem)
13. [Fases](#fases)
14. [Latency Budget](#latency-budget)
15. [Tech Stack](#tech-stack)
16. [Orchestrator Architectuur](#orchestrator-architectuur-open-vraag)
17. [Resources & Links](#resources--links)
18. [Design Decisions](#design-decisions-beantwoord)

---

## Vision

Een interactieve AI-gestuurde robotauto die:
- Luistert en reageert via spraak (conversational AI)
- Emoties toont op een OLED display
- Visueel kan waarnemen en reageren (camera/vision)
- Fysiek kan bewegen en interacteren

---

## Uitgangspunten

### Local-First

**Alles draait lokaal.** Dit is een bewuste keuze:

| Reden | Toelichting |
|-------|-------------|
| **Kosten** | Geen API costs, onbeperkt experimenteren |
| **Geen rate limiting** | Zo vaak testen als je wilt |
| **Privacy** | Geen data naar externe servers |
| **Snelheid** | Geen internet latency |
| **Leerzaam** | Meer fun om zelf te bouwen |
| **Offline capable** | Werkt ook zonder internet |

### Cloud-Ready (Optioneel)

Hoewel alles lokaal draait, is de architectuur **modulair** opgezet zodat elke service eenvoudig vervangen kan worden door een cloud alternatief:

| Lokale Service | Cloud Alternatief |
|----------------|-------------------|
| Voxtral (STT) | OpenAI Whisper API, Deepgram, AssemblyAI |
| Ministral (LLM) | OpenAI API, Anthropic, OpenRouter, Ollama Cloud |
| Piper (TTS) | ElevenLabs, OpenAI TTS, Google Cloud TTS |
| Wake Word (Porcupine) | - (blijft altijd lokaal op Pi) |

**Implementatie:** Elke service heeft een abstracte interface. Swap tussen local/cloud door environment variable of config.

```python
# Voorbeeld: STT service abstraction
class STTService(Protocol):
    async def transcribe(self, audio: bytes) -> str: ...

class VoxtralSTT(STTService):      # Lokaal
    ...

class OpenAIWhisperSTT(STTService): # Cloud fallback
    ...
```

### Modulair & Containerized

- **Elke service = aparte Docker container**
- **Loose coupling** via REST/WebSocket APIs
- **Onafhankelijk te testen** en te vervangen
- **Eerst desktop, dan Pi** - services die later op Pi draaien, starten als Docker container op desktop

---

## Use Cases

Elke use case beschrijft:
- **Trigger**: Wat start de interactie (spraak, detectie, timer, etc.)
- **Input**: Wat ontvangt de robot (audio, image, sensor data)
- **Processing**: Welke services worden aangesproken
- **Output**: Wat doet de robot (spraak, OLED, beweging)

---

### UC1: Basis Spraakinteractie

| Aspect | Details |
|--------|---------|
| **Trigger** | Voice: Wake word + vraag |
| **Input** | Audio via USB microfoon |
| **Processing** | STT → LLM → TTS |
| **Output** | Gesproken antwoord + OLED state |

**Scenario:**
```
TRIGGER:  User spreekt wake word "Hey robot"
          → Pi: wake word detected

INPUT:    User: "Wat is de hoofdstad van Frankrijk?"
          → Audio opname (VAD detecteert einde spraak)

PROCESSING:
  Pi      → Stuurt audio naar orchestrator
  STT     → "Wat is de hoofdstad van Frankrijk?"
  LLM     → Genereert: "De hoofdstad van Frankrijk is Parijs."
  TTS     → Converteert naar audio

OUTPUT:
  OLED    → listening (tijdens opname) → thinking (tijdens processing) → neutral
  Speaker → "De hoofdstad van Frankrijk is Parijs."
```

---

### UC2: Sentiment-Bewuste Reactie

| Aspect | Details |
|--------|---------|
| **Trigger** | Voice: Uitspraak met emotionele context |
| **Input** | Audio met positief/negatief sentiment |
| **Processing** | STT → LLM (sentiment analyse) → TTS + function call |
| **Output** | Passende respons + OLED emotie aangepast |

**Scenario (positief):**
```
TRIGGER:  Wake word

INPUT:    User: "Ik heb net gehoord dat ik die baan heb gekregen."

PROCESSING:
  STT     → Transcriptie
  LLM     → Detecteert: positief nieuws
          → Response: "Gefeliciteerd, goed nieuws."
          → Function call: show_emotion("happy")

OUTPUT:
  OLED    → happy
  Speaker → "Gefeliciteerd, goed nieuws."
```

**Scenario (negatief/stress):**
```
INPUT:    User: "De deadline is verschoven naar morgen, dat wordt lastig."

PROCESSING:
  LLM     → Detecteert: stressvolle situatie
          → Response: "Dat is krap. Kan ik ergens mee helpen?"
          → Function call: show_emotion("concerned")

OUTPUT:
  OLED    → concerned
  Speaker → "Dat is krap. Kan ik ergens mee helpen?"
```

---

### UC3: Bewegingscommando

| Aspect | Details |
|--------|---------|
| **Trigger** | Voice: Instructie voor fysieke actie |
| **Input** | Audio met bewegingsopdracht |
| **Processing** | STT → LLM → function call (move_robot) |
| **Output** | Bevestiging + motoractie |

**Scenario:**
```
TRIGGER:  Wake word

INPUT:    User: "Draai 90 graden naar links."

PROCESSING:
  STT     → Transcriptie
  LLM     → Herkent bewegingscommando
          → Function call: move_robot(action="turn_left", degrees=90)

OUTPUT:
  Speaker → "Begrepen."
  OLED    → focused
  Motors  → Draait 90 graden links
  Speaker → "Klaar."
  OLED    → neutral
```

---

### UC4: Visuele Analyse op Verzoek

| Aspect | Details |
|--------|---------|
| **Trigger** | Voice: Vraag over omgeving |
| **Input** | Audio + camera snapshot |
| **Processing** | STT + camera → LLM (multimodaal) → TTS |
| **Output** | Beschrijving van wat robot ziet |

**Scenario:**
```
TRIGGER:  Wake word

INPUT:    User: "Beschrijf wat je ziet."
          + Camera snapshot (automatisch bij vision-vraag)

PROCESSING:
  Pi      → Stuurt audio + image naar orchestrator
  STT     → Transcriptie
  LLM     → Analyseert image + vraag (Ministral multimodaal)
          → Genereert beschrijving

OUTPUT:
  OLED    → thinking (tijdens analyse)
  Speaker → "Ik zie een bureau met een monitor en toetsenbord.
             Links staat een bureaulamp, rechts een koffiemok."
  OLED    → neutral
```

---

### UC5: Gezichtsuitdrukking Analyse

| Aspect | Details |
|--------|---------|
| **Trigger** | Voice: Vraag over gezicht/uitdrukking |
| **Input** | Audio + camera snapshot (gezicht) |
| **Processing** | STT + Vision → LLM → TTS + emotie-mirroring |
| **Output** | Analyse + OLED spiegelt expressie |

**Scenario:**
```
TRIGGER:  Wake word

INPUT:    User: "Hoe kijk ik?"
          + Camera snapshot

PROCESSING:
  LLM     → Analyseert gezichtsuitdrukking in image
          → Detecteert: geconcentreerd/neutraal
          → Function call: show_emotion("neutral")

OUTPUT:
  Speaker → "Je kijkt geconcentreerd. Druk bezig?"
  OLED    → neutral (spiegelt gebruiker)
```

---

### UC6: Object Detection Trigger (Proactief)

| Aspect | Details |
|--------|---------|
| **Trigger** | Vision: YOLO detecteert verandering (bijv. persoon verschijnt) |
| **Input** | Continuous YOLO op Pi → detection event |
| **Processing** | Detection → Orchestrator → LLM beslist reactie |
| **Output** | Proactieve melding |

**Scenario:**
```
TRIGGER:  YOLO detecteert: "person" (confidence: 0.94)
          Vorige state: geen persoon in beeld

INPUT:    Detection metadata naar orchestrator:
          {label: "person", confidence: 0.94, appeared: true}

PROCESSING:
  Orchestrator → Evalueert: nieuwe persoon = relevante gebeurtenis
  LLM          → Genereert gepaste reactie

OUTPUT:
  OLED    → alert
  Speaker → "Iemand is binnengekomen."
  Motors  → Camera richt naar gedetecteerde persoon (optioneel)
```

---

### UC7: Gecombineerde Metadata + Vision

| Aspect | Details |
|--------|---------|
| **Trigger** | Voice: Vraag, met YOLO metadata als extra context |
| **Input** | Audio + image + object detection labels |
| **Processing** | STT + Vision + Metadata → LLM |
| **Output** | Contextrijke beschrijving |

**Scenario:**
```
TRIGGER:  Wake word

INPUT:    User: "Wat staat er op mijn bureau?"
          + Image
          + YOLO metadata: [
              {label: "laptop", confidence: 0.91},
              {label: "cup", confidence: 0.85},
              {label: "book", confidence: 0.79}
            ]

PROCESSING:
  LLM     → Ontvangt: vraag + image + gestructureerde metadata
          → Metadata helpt focussen, image geeft details

OUTPUT:
  Speaker → "Op je bureau zie ik een laptop, een kopje, en wat lijkt op een boek
             of notitieboek aan de rechterkant."
```

---

### UC8: Navigatie met Realtime Feedback

| Aspect | Details |
|--------|---------|
| **Trigger** | Voice: Navigatie-opdracht |
| **Input** | Audio + continuous sensor data (ultrasonic) |
| **Processing** | Bewegingsuitvoering + obstakelvermijding |
| **Output** | Beweging + gesproken status updates |

**Scenario:**
```
TRIGGER:  Wake word

INPUT:    User: "Rijd vooruit tot je iets tegenkomt."

PROCESSING:
  LLM     → Function call: move_robot(action="forward", until="obstacle")
  Pi      → Voert uit met continue ultrasonic monitoring

OUTPUT (tijdlijn):
  t=0s:   Speaker → "Ik begin te rijden."
          Motors  → Vooruit
          OLED    → focused

  t=3s:   [Ultrasonic: 30cm]
          Speaker → "Ik nader een obstakel."

  t=4s:   [Ultrasonic: 15cm - threshold]
          Motors  → Stop
          Speaker → "Gestopt. Obstakel op 15 centimeter."
          OLED    → neutral
```

---

### UC9: Proactieve Idle-Interactie

| Aspect | Details |
|--------|---------|
| **Trigger** | Timer: Inactiviteit + persoon aanwezig |
| **Input** | Tijd sinds laatste interactie + YOLO detection |
| **Processing** | Orchestrator evalueert → besluit tot initiatief |
| **Output** | Robot start conversatie |

**Scenario:**
```
TRIGGER:  - Laatste interactie: 10 minuten geleden
          - YOLO: persoon in beeld (continue)
          - Config: proactive_mode = true

PROCESSING:
  Orchestrator → Idle timeout + user present = proactieve trigger
  LLM          → Genereert context-geschikte opening

OUTPUT:
  OLED    → curious
  Speaker → "Je bent al een tijdje bezig. Kan ik ergens mee helpen?"
  OLED    → listening (wacht op response)

  [Geen response binnen 10 sec]
  OLED    → neutral
  State   → Terug naar idle
```

---

## Robot State & Situational Awareness

### Waarom Dit Belangrijk Is

In tegenstelling tot een VR-app of chatbot, heeft de robot een **fysieke staat** die invloed heeft op interacties:

| Vraag | Overwegingen |
|-------|--------------|
| Staat de robot stil tijdens een vraag? | Audio capture is beter zonder motorgeluid |
| Wat als de robot rijdt tijdens een commando? | Moet hij stoppen? Doorrijden? |
| Hoe weet het LLM wat de robot "ziet"? | Object detection metadata, foto's, of beide? |
| Wat als er een obstakel is? | Ultrasonic sensor, object detection, of beide? |

### Robot States

```
┌─────────────┐     wake word      ┌─────────────┐
│    IDLE     │ ─────────────────► │  LISTENING  │
│  (standby)  │                    │  (opnemen)  │
└─────────────┘                    └──────┬──────┘
      ▲                                   │
      │                                   │ audio complete
      │                                   ▼
      │                            ┌─────────────┐
      │                            │  THINKING   │
      │                            │ (processing)│
      │                            └──────┬──────┘
      │                                   │
      │         ┌─────────────────────────┼─────────────────────────┐
      │         │                         │                         │
      │         ▼                         ▼                         ▼
      │   ┌───────────┐           ┌─────────────┐           ┌─────────────┐
      │   │ SPEAKING  │           │   MOVING    │           │   ACTING    │
      │   │(TTS play) │           │ (motors on) │           │(func calls) │
      │   └─────┬─────┘           └──────┬──────┘           └──────┬──────┘
      │         │                        │                         │
      └─────────┴────────────────────────┴─────────────────────────┘
                              done
```

### State-Aware Beslissingen

| Huidige State | Nieuw Commando | Gedrag |
|---------------|----------------|--------|
| IDLE | "Hey robot" | → LISTENING |
| MOVING | "Hey robot" | Stop beweging → LISTENING |
| SPEAKING | "Hey robot" | Pauzeer TTS → LISTENING (of negeer?) |
| LISTENING | Stilte (timeout) | → IDLE |
| ANY | Obstakel gedetecteerd | Stop beweging, meld aan gebruiker |

### Context Data naar Orchestrator

Bij elk request kan de Pi metadata meesturen:

```json
{
  "audio": "<blob>",
  "image": "<blob>",  // optioneel
  "state": {
    "current": "IDLE",
    "battery_level": 85,
    "is_moving": false,
    "obstacle_detected": false,
    "distance_front_cm": 45
  },
  "detections": [  // van YOLO op Pi
    {"label": "person", "confidence": 0.92},
    {"label": "chair", "confidence": 0.78}
  ],
  "conversation_id": "abc123"
}
```

Dit geeft het LLM context om betere beslissingen te nemen.

---

## Aanpak

### Ontwikkel Filosofie

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EERST: ALLES OP DESKTOP                          │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Docker   │  │ Docker   │  │ Docker   │  │ Docker   │            │
│  │ Wake     │  │ STT      │  │ LLM      │  │ TTS      │            │
│  │ Word*    │  │ Voxtral  │  │Ministral │  │ Piper    │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
│       │              │             │             │                  │
│       └──────────────┴─────────────┴─────────────┘                  │
│                              │                                       │
│                    ┌─────────┴─────────┐                            │
│                    │   Orchestrator    │                            │
│                    │   (FastAPI)       │                            │
│                    └─────────┬─────────┘                            │
│                              │                                       │
│                    ┌─────────┴─────────┐                            │
│                    │  Desktop Mockup   │                            │
│                    │  - Pygame OLED    │                            │
│                    │  - Desktop mic    │                            │
│                    │  - Desktop speaker│                            │
│                    └───────────────────┘                            │
│                                                                      │
│  * Wake word simuleert we eerst, of gebruiken push-to-talk          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Fase 3: Hardware integratie
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LATER: PI 5 INTEGRATIE                           │
│                                                                      │
│  Services die naar Pi verhuizen:                                    │
│  - Wake word (Porcupine)                                            │
│  - Audio capture                                                     │
│                                                                      │
│  Services die MOGELIJK naar Pi verhuizen:                           │
│  - TTS: verhuist naar Pi als Piper (of ander lightweight) voldoet,  │
│         anders blijft TTS als zwaardere service op desktop          │
│  - OLED control                                                      │
│  - Motor/servo control                                               │
│  - Camera capture                                                    │
│                                                                      │
│  Services die op Desktop blijven:                                   │
│  - Orchestrator                                                      │
│  - STT (Voxtral) - te zwaar voor Pi                                 │
│  - LLM (Ministral) - te zwaar voor Pi                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Waarom Eerst Desktop?

1. **Sneller itereren** - geen SD card flashen, SSH sessions, etc.
2. **Makkelijker debuggen** - alle logs direct zichtbaar
3. **Hardware onafhankelijk** - werkt ook als Pi nog niet binnen is
4. **Gefaseerd testen** - elke service apart valideren
5. **Mockups** - OLED simulator, fake motor output

---

## Hardware Setup

### Desktop (AI Processing Server)
| Component | Specs | Rol |
|-----------|-------|-----|
| GPU 1 | RTX 4090 (24GB VRAM) | Primaire inference - modellen met hoogste VRAM behoefte |
| GPU 2 | RTX 5070 Ti (~12GB effectief*) | Secundair / overflow indien nodig |
| RAM | 64GB | Model loading, context |
| Docker | Microservices | Orchestrator, model serving |

*RTX 5070 Ti heeft 16GB VRAM, maar ~4GB gaat naar OS/monitor, dus effectief ~12GB beschikbaar.

**GPU Strategie (te bepalen):**
- Idealiter draait alles op de RTX 4090 voor minimale latency (geen GPU-to-GPU communicatie)
- RTX 5070 Ti als overflow/headroom indien modellen niet passen
- Exacte verdeling hangt af van: model sizes, context lengths, concurrent requests
- Experimenteren nodig om optimale configuratie te vinden

### Robot (Pi 5 Client)
| Component | Specs | Rol |
|-----------|-------|-----|
| Raspberry Pi 5 | 16GB RAM | Edge processing, I/O control |
| PiCar-X Kit | v2.0 | Motors, servo's, ultrasonic |
| Camera | OV5647 via CSI | Vision input |
| OLED | 0.96" I2C (128x64) | Emotie display |
| USB Mic | Omnidirectioneel | Audio input |
| Speaker | Robot HAT I2S | Audio output |

---

## Model Rollen - Verduidelijkt

### Overzicht: Welk Model Doet Wat?

| Model | Taak | Input | Output | Waar | Wanneer |
|-------|------|-------|--------|------|---------|
| **Wake Word** | Trigger detectie | Audio stream | Activatie signaal | Pi (lokaal) | Altijd actief |
| **STT** | Speech-to-Text | Audio blob | Tekst transcriptie (+ evt. function calls) | Desktop | Na wake word |
| **Object Detection** | Realtime detectie | Camera stream | Labels + bounding boxes | Pi (lokaal) | Continu of on-demand |
| **Ministral 8B/14B** | "Hersenen" - vision + redeneren + function calling | Tekst + image + metadata + context | Antwoord + function calls | Desktop | Na STT |
| **TTS** | Text-to-Speech | Tekst | Audio | Desktop of Pi | Na LLM response |

### STT Opties (Open Vraag)

| Optie | Voordelen | Nadelen | Status |
|-------|-----------|---------|--------|
| **Voxtral Mini** | Function calling mogelijk, goede accuracy | Zwaarder, nieuwer (minder getest) | Kandidaat |
| **faster-whisper** | Lightweight, bewezen, snel | Geen native function calling | Kandidaat |
| **Whisper Large v3** | Beste accuracy | Zwaarder dan faster-whisper | Fallback |

**Open vragen:**
- Als we geen function calling vanuit STT gebruiken, is faster-whisper dan de betere keuze (lichter)?
- Voxtral function calling KAN nuttig zijn (bijv. sentiment detectie, urgentie in stem) - optie openhouden
- Experimenteren nodig om te bepalen welke STT het beste past

### Ministral 8B/14B als "Hersenen"

- **Multimodaal**: kan zowel tekst als images verwerken
- **Function calling**: native support voor tool calls
- **Alles-in-één**: geen aparte vision → LLM pipeline nodig
- Krijgt: transcriptie + image (optioneel) + object detection metadata + conversation history + tools
- Genereert: antwoord + function calls

### Object Detection op Pi (Nieuw)

Naast het sturen van foto's naar Ministral voor analyse, kunnen we **lightweight object detection** op de Pi zelf draaien:

| Aspect | Details |
|--------|---------|
| **Model** | YOLO (Nano/Small), MobileNet-SSD, of vergelijkbaar |
| **Doel** | Realtime detectie: persoon, dier, object, gezicht |
| **Output** | Labels + confidence + bounding boxes |
| **Gebruik** | Metadata meesturen naar orchestrator |

**Voordelen:**
- Snelle feedback zonder desktop roundtrip
- Robot "weet" wat er voor hem is, ook zonder expliciete vraag
- Kan triggers zijn voor proactief gedrag
- Minder data naar desktop (alleen metadata, niet altijd full image)

**Use cases:**
- "Er staat een persoon voor me" → Robot kijkt naar persoon
- "Ik zie een kat" → Robot reageert enthousiast
- Gezicht gedetecteerd → Activeer vision-gerelateerde functies

### TTS Opties (Te Bepalen)

**Primair: TTS op Desktop (Docker service)**
- Meer rekenkracht beschikbaar
- Betere kwaliteit mogelijk
- Opties: Coqui XTTS, Edge TTS, of andere

**Secundair: TTS op Pi (latency optimalisatie)**
- Scheelt network roundtrip (~40ms)
- Opties: Piper, espeak-ng
- **Let op:** Piper klinkt mogelijk "houterig" - uitproberen nodig

**Aanpak:** Start met TTS op desktop, experimenteer met kwaliteit. Later eventueel naar Pi verhuizen als latency kritiek wordt en kwaliteit acceptabel is.

---

## Architectuur

### High-Level Overzicht

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              PI 5 (CLIENT)                               │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │ Wake Word  │  │    Mic     │  │  Camera    │  │    Pi Client       │ │
│  │ (Porcupine)│  │   Input    │  │   Input    │  │                    │ │
│  │  LOKAAL    │  └─────┬──────┘  └─────┬──────┘  │  - Audio capture   │ │
│  └─────┬──────┘        │               │         │  - Wake word mgmt  │ │
│        │               │               │         │  - Function exec   │ │
│        ▼               ▼               ▼         └─────────┬──────────┘ │
│  [Activatie]     [Audio blob]    [Image blob]              │            │
│        │               │               │                   │            │
│        └───────────────┴───────────────┴───────────────────┘            │
│                                        │                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                         │
│  │   Piper    │  │   OLED     │  │  Motors/   │  ◄── Function calls    │
│  │    TTS     │  │  Display   │  │  Servo's   │                         │
│  │  LOKAAL    │  └────────────┘  └────────────┘                         │
│  └────────────┘                                                          │
│        │                                                                 │
│  ┌────────────┐                                                          │
│  │  Speaker   │                                                          │
│  └────────────┘                                                          │
└────────────────────────────────────────┬────────────────────────────────┘
                                         │ WebSocket (LAN)
                                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         DESKTOP SERVER                                  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      ORCHESTRATOR (FastAPI)                       │  │
│  │                                                                   │  │
│  │  1. Ontvang request: { audio, image?, context }                  │  │
│  │  2. Audio → Voxtral → Transcriptie                               │  │
│  │  3. Transcriptie + Image → Ministral → Response + Function Calls │  │
│  │  4. Stuur response + function calls terug naar Pi                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│           │                              │                              │
│           ▼                              ▼                              │
│  ┌──────────────────┐          ┌──────────────────┐                    │
│  │     Voxtral      │          │    Ministral     │                    │
│  │     Mini 3B      │ ──────►  │     8B/14B       │                    │
│  │                  │          │                  │                    │
│  │   Audio → Text   │          │  Text + Image    │                    │
│  │                  │          │  → Response      │                    │
│  │    RTX 4090      │          │  + Func Calls    │                    │
│  │                  │          │                  │                    │
│  │                  │          │  RTX 4090/5070Ti │                    │
│  └──────────────────┘          └──────────────────┘                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Gedetailleerde Processing Flow

> **Note:** Tijden in dit diagram zijn **illustratieve schattingen**, geen gemeten waarden.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              STAP 1: PI                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Wake word detectie (Porcupine - draait lokaal, ~5% CPU)                │
│  └─> "Hey robot" gedetecteerd                                           │
│                                                                          │
│  Start audio opname (VAD - Voice Activity Detection)                    │
│  └─> Wacht tot gebruiker klaar is met praten                            │
│                                                                          │
│  [Optioneel] Camera snapshot (als vision relevant)                      │
│                                                                          │
│  Stuur naar orchestrator:                                               │
│  {                                                                       │
│    "audio": <blob>,                                                     │
│    "image": <blob> | null,                                              │
│    "context": { "conversation_id": "...", "sensors": {...} }            │
│  }                                                                       │
│                                                                          │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         STAP 2: ORCHESTRATOR                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STAP 2a: SPEECH-TO-TEXT                                                │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                                                                  │    │
│  │  Audio → Voxtral Mini                                           │    │
│  │                                                                  │    │
│  │  Input: audio blob                                              │    │
│  │  Output: "Kijk eens naar me, lach ik?"                          │    │
│  │                                                                  │    │
│  │  ~200-500ms (schatting)                                          │    │
│  │                                                                  │    │
│  └───────────────────────────────────┬─────────────────────────────┘    │
│                                      │                                   │
│                                      ▼                                   │
│  STAP 2b: MINISTRAL (Multimodaal - Text + Vision + Function Calling)   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                                                                  │    │
│  │  Input:                                                          │    │
│  │  - Transcriptie: "Kijk eens naar me, lach ik?"                  │    │
│  │  - Image: <camera snapshot> (indien aanwezig)                   │    │
│  │  - Conversation history                                          │    │
│  │  - Available tools: [show_emotion, move_robot, ...]             │    │
│  │  - System prompt: "Je bent een vriendelijke robot companion..." │    │
│  │                                                                  │    │
│  │  Ministral 8B/14B ziet ZOWEL de tekst ALS de afbeelding         │    │
│  │  en kan direct beslissen over function calls                     │    │
│  │                                                                  │    │
│  │  Output:                                                         │    │
│  │  {                                                               │    │
│  │    "text": "Ja! Ik zie dat je lacht, dat maakt mij ook blij!",  │    │
│  │    "function_calls": [                                           │    │
│  │      { "name": "show_emotion", "args": { "emotion": "happy" }}  │    │
│  │    ]                                                             │    │
│  │  }                                                               │    │
│  │                                                                  │    │
│  │  ~300-800ms (schatting)                                          │    │
│  │                                                                  │    │
│  └───────────────────────────────────┬─────────────────────────────┘    │
│                                      │                                   │
│                                      ▼                                   │
│  Totaal orchestrator: ~500-1300ms (schatting)                           │
│                                                                          │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              STAP 3: PI                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Ontvang response:                                                       │
│  {                                                                       │
│    "text": "Ja! Ik zie dat je lacht, dat maakt mij ook blij!",          │
│    "function_calls": [                                                   │
│      { "name": "show_emotion", "args": { "emotion": "happy" }}          │
│    ]                                                                     │
│  }                                                                       │
│                                                                          │
│  PARALLEL UITVOERING:                                                    │
│                                                                          │
│  ┌─────────────────────────┐    ┌─────────────────────────┐             │
│  │                         │    │                         │             │
│  │  Text → TTS             │    │  Function Calls         │             │
│  │  (Desktop of Pi - TBD)  │    │  Uitvoeren              │             │
│  │                         │    │                         │             │
│  │  Output: audio          │    │  → OLED: emotie         │             │
│  │  → Speaker afspelen     │    │  → Motors: beweging     │             │
│  │                         │    │  → Sounds: effecten     │             │
│  │  ~150-300ms             │    │  ~50ms                  │             │
│  │                         │    │                         │             │
│  └─────────────────────────┘    └─────────────────────────┘             │
│                                                                          │
│  TOTALE LATENCY: ~1-3 sec (schatting, moet gemeten worden)              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Wake Word Opties (Pi Lokaal)

| Optie | Pros | Cons | Aanbevolen |
|-------|------|------|------------|
| **Picovoice Porcupine** | Zeer accuraat, custom wake words, gratis voor hobby | Closed source | ✅ Ja |
| **OpenWakeWord** | Open source, custom trainbaar | Minder accuraat | Alternatief |
| **Snowboy** | Populair, custom wake words | Niet meer onderhouden | Nee |
| **Vosk** | Open source, offline | Meer resources nodig | Voor later |

**Aanbeveling:** Start met Porcupine. Gratis voor non-commercial, custom wake word ("Hey Robot").

---

## TTS Opties (Open Vraag)

### Aanpak

```
1. Start: TTS als Docker service op desktop
   └── Experimenteer met kwaliteit en latency

2. Evalueer: Welke TTS klinkt het beste in het Nederlands?
   └── Probeer meerdere opties, focus op natuurlijke klank

3. Later: Overweeg TTS op Pi alleen als:
   └── Latency van desktop TTS te hoog is
   └── EN kwaliteit van Pi TTS acceptabel is
```

### Desktop TTS Opties (Primair - waar we starten)

| Optie | Nederlands | Kwaliteit | Offline | Notes |
|-------|------------|-----------|---------|-------|
| **Coqui XTTS** | ✅ Ja | Zeer goed | ✅ | Voice cloning mogelijk, zwaarder |
| **Bark** | ✅ Ja | Goed | ✅ | Open source, expressief |
| **Edge TTS** | ✅ Ja | Excellent | ❌ | Microsoft API, vereist internet |

### Pi TTS Opties (Alleen indien nodig)

| Optie | Nederlands | Kwaliteit | Notes |
|-------|------------|-----------|-------|
| **Piper** | ✅ Ja | Matig | Snel, maar kan "houterig" klinken |
| **espeak-ng** | ✅ Ja | Basis | Zeer snel, klinkt robotachtig |

**Let op:** Piper is **niet** de eerste keuze. Desktop TTS blijft primair tenzij:
- Desktop TTS latency > ~500ms toevoegt
- Piper kwaliteit acceptabel blijkt na grondig testen

---

## Function Calling Schema

```json
{
  "tools": [
    {
      "name": "show_emotion",
      "description": "Toon een emotie op het OLED scherm van de robot",
      "parameters": {
        "type": "object",
        "properties": {
          "emotion": {
            "type": "string",
            "enum": ["happy", "sad", "thinking", "surprised", "angry", "love", "confused", "sleeping", "excited", "neutral"],
            "description": "De emotie om te tonen"
          },
          "intensity": {
            "type": "string",
            "enum": ["subtle", "normal", "exaggerated"],
            "default": "normal"
          }
        },
        "required": ["emotion"]
      }
    },
    {
      "name": "move_robot",
      "description": "Beweeg de robot fysiek",
      "parameters": {
        "type": "object",
        "properties": {
          "action": {
            "type": "string",
            "enum": ["forward", "backward", "turn_left", "turn_right", "spin", "nod_yes", "shake_no", "look_around", "dance", "stop"]
          },
          "speed": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 50
          },
          "duration_ms": {
            "type": "integer",
            "minimum": 100,
            "maximum": 5000,
            "default": 1000
          }
        },
        "required": ["action"]
      }
    },
    {
      "name": "play_sound",
      "description": "Speel een geluidseffect af",
      "parameters": {
        "type": "object",
        "properties": {
          "sound": {
            "type": "string",
            "enum": ["beep", "happy_tune", "sad_tune", "alert", "greeting", "goodbye", "thinking", "error"]
          }
        },
        "required": ["sound"]
      }
    },
    {
      "name": "take_photo",
      "description": "Maak een foto met de camera voor visuele analyse",
      "parameters": {
        "type": "object",
        "properties": {
          "analyze": {
            "type": "boolean",
            "default": true,
            "description": "Of de foto geanalyseerd moet worden door het vision model"
          },
          "describe": {
            "type": "string",
            "description": "Specifieke vraag over wat te beschrijven in de foto"
          }
        }
      }
    },
    {
      "name": "look_at",
      "description": "Richt de camera/hoofd naar een specifieke richting",
      "parameters": {
        "type": "object",
        "properties": {
          "direction": {
            "type": "string",
            "enum": ["left", "right", "up", "down", "center", "user"]
          }
        },
        "required": ["direction"]
      }
    }
  ]
}
```

---

## OLED Emotie Systeem

### Hardware: 0.96" I2C OLED (128x64, Monochroom)

**Let op:** Dit is een **monochroom (1-bit) display**, niet een full-color scherm.
- Resolutie: 128x64 pixels
- Kleuren: Alleen zwart en wit (of zwart en blauw/geel afhankelijk van panel)
- Controller: Waarschijnlijk SSD1306
- Library: `luma.oled` (Python)

### Emotie Assets

Assets moeten **1-bit zwart/wit** zijn, geen grijstinten of kleuren.

**Formaat opties:**
- PNG (1-bit) - makkelijk te editen, converteren naar bitmap bij laden
- BMP (1-bit) - native bitmap formaat
- Python code - direct pixels tekenen met `luma.oled` primitives

```
assets/emotions/
├── happy.png        Standaard blij (ogen + mond)
├── happy_big.png    Breed lachend
├── sad.png          Verdrietig
├── thinking.png     Denkend (basisframe, animatie in code)
├── surprised.png    Verrast (grote ogen)
├── angry.png        Boos
├── love.png         Hartjes ogen
├── confused.png     Verward
├── sleeping.png     Slapend (basisframe, Zzz animatie in code)
├── excited.png      Enthousiast
├── neutral.png      Neutraal/standby
└── listening.png    Luisterend (na wake word)
```

**Ontwerprichtlijnen:**
- Houd het simpel: dikke lijnen, duidelijke vormen
- Test op echt display: wat er op een monitor goed uitziet kan op 128x64 onduidelijk zijn
- Animaties: basisframes als assets, beweging in code (blink, bounce, etc.)

### Animaties

| Trigger | Animatie | Frames |
|---------|----------|--------|
| Luisteren | Ogen knipperen, pulserende "listening" indicator | 3-4 |
| Denken | Ogen naar boven, roterende dots | 4-6 |
| Praten | Mond beweging (open/dicht sync met audio amplitude) | 2-3 |
| Idle | Occasioneel knipperen, kleine oogbewegingen | 2 |
| Transition | Fade tussen emoties | 2-3 |

---

## Fases

> **Principe:** Alles wordt eerst als Docker container op desktop gebouwd en getest.
> Pas in Fase 3 verhuizen bepaalde services naar de Pi.

### Fase 0: Voorbereiding (Nu - Voordat hardware binnenkomt)

**Doel:** Desktop simulatie zonder hardware

- [ ] Ontwerp finaliseren (dit document)
- [ ] OLED emotie assets maken (128x64 PNG's)
- [ ] Desktop mockup bouwen:
  - Pygame/Tkinter window als OLED simulator
  - Desktop mic als input
  - Desktop speakers als output
- [ ] Project structuur opzetten (monorepo met services/)

**Deliverables:**
- Emotie PNG assets (11+ emoties)
- OLED simulator script (Python)
- Basis project structuur

```
picar-x-ai/
├── docker-compose.yml
├── services/
│   ├── orchestrator/     # FastAPI
│   ├── stt/              # Voxtral
│   ├── llm/              # Ministral via Ollama
│   └── tts/              # TTS service (locatie te bepalen)
├── desktop-mockup/       # Simulators voor OLED, motors
├── pi-client/            # Komt in Fase 3
└── assets/
    └── emotions/         # PNG files
```

---

### Fase 1: Audio Pipeline (Desktop Only)

**Doel:** Werkende spraak-naar-spraak loop, volledig in Docker

```
[Desktop Mic] → [STT Container] → [LLM Container] → [TTS Container] → [Desktop Speaker]
```

**Docker Services:**
```yaml
services:
  orchestrator:
    build: ./services/orchestrator
    ports: ["8000:8000"]

  stt:
    # Voxtral Mini via vLLM of dedicated image
    # OF: tijdelijk faster-whisper als Voxtral nog niet klaar

  llm:
    # Ministral 8B/14B via Ollama
    image: ollama/ollama
    volumes: ["./models:/root/.ollama"]

  tts:
    # TTS engine (te bepalen: Piper, Coqui XTTS, Bark, etc.)
    # Blijft op desktop tenzij lightweight optie voldoet voor Pi
```

**Stappen:**
- [ ] Docker compose opzetten met alle services
- [ ] STT service: Voxtral Mini (of Whisper als fallback)
- [ ] LLM service: Ministral 8B/14B via Ollama
- [ ] TTS service: experimenteren met opties (Piper, Coqui, etc.)
- [ ] Orchestrator: FastAPI die services aanstuurt
- [ ] Simpele CLI of web interface voor testen
- [ ] Basis conversatie werkend (tekst in → tekst uit → audio uit)

**Test criteria:**
- Zeg iets → krijg gesproken antwoord
- Latency < 2 seconden end-to-end
- Conversation history werkt (meerdere beurten)
- Elke service apart testbaar via API

---

### Fase 2: Function Calling + Emoties (Desktop Simulatie)

**Doel:** LLM triggert acties via function calls, getest met desktop simulators

**Nieuwe componenten:**
```
desktop-mockup/
├── oled_simulator.py    # Pygame window 128x64
├── motor_simulator.py   # Console output of animatie
└── sound_player.py      # Desktop audio voor geluidseffecten
```

**Stappen:**
- [ ] Function calling schema toevoegen aan Ministral prompts
- [ ] Orchestrator parsed en routeert function calls
- [ ] OLED simulator (Pygame window) reageert op `show_emotion`
- [ ] Motor simulator (console/pygame) reageert op `move_robot`
- [ ] Sound player voor `play_sound` function calls
- [ ] Testen met emotionele zinnen en commando's

**Test criteria:**
- "Dankjewel!" → OLED simulator toont love emotie
- "Ik ben verdrietig" → OLED simulator toont sad emotie
- "Draai eens rond" → Motor simulator toont beweging
- Function calls komen NAAST tekst response
- Meerdere function calls in één response mogelijk

---

### Fase 3: Pi 5 Integratie

**Doel:** Echte hardware, services gesplitst tussen Pi en Desktop

**Wat verhuist naar Pi:**
| Component | Van | Naar | Reden |
|-----------|-----|------|-------|
| Wake word | Desktop mock | Pi (Porcupine) | Moet altijd luisteren, lokaal |
| Audio capture | Desktop mic | Pi (USB mic) | Fysieke locatie |

**Wat MOGELIJK naar Pi verhuist:**
| Component | Conditie | Anders |
|-----------|----------|--------|
| TTS | Als Piper of ander lightweight voldoet | Blijft op desktop als zwaardere TTS nodig is |
| OLED control | Pygame simulator | Pi (luma.oled) | Hardware |
| Motor control | Console simulator | Pi (picar-x lib) | Hardware |
| Camera | - | Pi (picamera2) | Hardware |

**Wat op Desktop blijft:**
| Component | Reden |
|-----------|-------|
| Orchestrator | Centrale logica |
| STT (Voxtral) | Te zwaar voor Pi |
| LLM (Ministral) | Te zwaar voor Pi |

**Stappen:**
- [ ] PiCar-X assembleren en basis examples runnen
- [ ] Pi client applicatie bouwen (`pi-client/`)
- [ ] Wake word (Porcupine) installeren en testen
- [ ] Audio capture via USB mic
- [ ] WebSocket verbinding met desktop orchestrator
- [ ] TTS integratie (Pi of desktop, afhankelijk van gekozen engine)
- [ ] OLED driver (luma.oled) implementeren
- [ ] Motor/servo control via picar-x library
- [ ] Function call handlers (OLED, motors, sounds)

**Test criteria:**
- Wake word "Hey robot" activeert luisteren
- Hele flow werkt: spraak → desktop → antwoord + emotie op Pi
- Latency acceptabel voor conversatie (exacte target te bepalen)
- Robot beweegt op commando

---

### Fase 4: Vision Activeren

**Doel:** Camera input voor context-aware interactie

*Note: Ministral 8B/14B ondersteunt vision al - we hoeven alleen de camera pipeline toe te voegen*

**Stappen:**
- [ ] Camera capture op Pi (libcamera / picamera2)
- [ ] Image meesturen naar orchestrator (JPEG, gecomprimeerd)
- [ ] Orchestrator stuurt image mee naar Ministral
- [ ] "Wat zie je?" en "Kijk naar me" commando's

**Test criteria:**
- "Kijk naar me, lach ik?" → Correct antwoord
- Vision context beïnvloedt emotie response
- Latency blijft < 1.5 sec

---

### Fase 4b: Object Detection op Pi (Optioneel)

**Doel:** Lightweight realtime object detection lokaal op Pi

**Waarom apart van LLM vision?**
- LLM vision: diepgaande analyse ("beschrijf wat je ziet")
- Object detection: snelle labels ("persoon gedetecteerd")
- Kunnen naast elkaar bestaan en elkaar aanvullen

**Stappen:**
- [ ] YOLO Nano/Small model op Pi installeren (ultralytics)
- [ ] Camera stream → continuous detection
- [ ] Detection results als metadata naar orchestrator
- [ ] Triggers voor proactief gedrag (persoon gezien, etc.)
- [ ] Combinatie: YOLO labels + LLM vision voor rijke context

**Test criteria:**
- Detecteert personen, dieren, objecten met >80% accuracy
- Draait op Pi zonder significante vertraging
- Metadata komt correct aan bij orchestrator

**Use cases:**
```python
# Voorbeeld metadata van Pi
{
  "detections": [
    {"label": "person", "confidence": 0.94, "bbox": [100, 50, 200, 300]},
    {"label": "cat", "confidence": 0.87, "bbox": [300, 200, 100, 150]}
  ],
  "timestamp": "2026-01-10T12:34:56Z"
}
```

---

### Fase 5: Autonomie & Polish

**Doel:** Personality en autonome gedragingen

**Features:**
- [ ] Idle behaviors (rondkijken, knipperen)
- [ ] Proactieve interactie ("Je bent al even stil...")
- [ ] Personality tuning via system prompts
- [ ] Conversation memory (langere termijn)
- [ ] Obstacle avoidance (ultrasonic sensor)
- [ ] Battery status awareness

---

## Latency Budget

> **⚠️ DISCLAIMER:** Onderstaande waarden zijn **schattingen/illustraties**, NIET gemeten.
> De werkelijke latency hangt af van: model sizes, GPU load, network condities, context length, etc.
> Dit dient alleen om de relatieve impact van verschillende stappen te illustreren.

| Stap | Geschat | Notes |
|------|---------|-------|
| Wake word detection | ~50ms | Pi lokaal, lightweight |
| Audio capture (VAD) | ~500ms+ | Wacht op einde spraak (variabel) |
| Network Pi→Desktop | ~10-50ms | LAN, afhankelijk van payload size |
| STT | ~200-500ms | Afhankelijk van model (faster-whisper vs Voxtral) |
| LLM (Ministral) | ~300-800ms | Sterk afhankelijk van context length + image |
| Network Desktop→Pi | ~10-30ms | Kleinere payload (alleen tekst + JSON) |
| TTS | ~100-500ms | Sterk afhankelijk van TTS engine en locatie |
| Audio playback start | ~50ms | Buffer filling |
| **TOTAL (geschat)** | **~1-3 sec** | Breed bereik, moet gemeten worden |

**Waar kunnen we winnen?**

| Optimalisatie | Geschatte impact | Trade-off |
|---------------|------------------|-----------|
| TTS op Pi i.p.v. Desktop | -50-200ms | Mogelijk lagere kwaliteit |
| Kleinere STT model | -100-200ms | Mogelijk lagere accuracy |
| Kleinere LLM model | -200-400ms | Mogelijk lagere kwaliteit antwoorden |
| Audio streaming i.p.v. batch | -200-500ms | Complexere implementatie |

**Conclusie:** Exacte waarden moeten gemeten worden zodra we werkende services hebben. Latency optimalisatie is een iteratief proces.

---

## Tech Stack

### Pi 5 Client
- **Python 3.11+**
- **picovoice** - Wake word (Porcupine)
- **pyaudio** - Audio capture
- **TTS** - Te bepalen (Piper, of audio van desktop)
- **luma.oled** - OLED display
- **picar-x** - Robot control (SunFounder library)
- **ultralytics** - YOLO voor object detection (optioneel)
- **websockets** - Server communicatie

### Desktop Server
- **Docker Compose** - Container orchestration
- **FastAPI** - Orchestrator API
- **Model Serving** - Zie tabel hieronder
- **TTS service** - Te bepalen welke

### Model Serving Frameworks

| Model | Framework | Reden | Alternatief |
|-------|-----------|-------|-------------|
| **Voxtral** | **vLLM** | Mistral modellen draaien goed op vLLM, Ollama support onzeker | HuggingFace Transformers |
| **faster-whisper** | **Dedicated container** | Eigen optimized runtime (CTranslate2) | - |
| **Ministral 8B/14B** | **Ollama** of **vLLM** | Ollama = simpeler setup, vLLM = sneller | LlamaCPP, HF Transformers |
| **YOLO** | **Ultralytics** | Native library, draait op Pi | - |
| **TTS** | **Dedicated container** | Afhankelijk van gekozen TTS engine | - |

**Ollama vs vLLM:**

| Aspect | Ollama | vLLM |
|--------|--------|------|
| Setup | Simpel, één binary | Complexer, Python |
| Model support | Veel GGUF modellen | Meer HuggingFace modellen |
| Performance | Goed | Beter (continuous batching) |
| API | Eigen API + OpenAI compatible | OpenAI compatible |
| Voxtral support | ❓ Onzeker | ✅ Ja |
| Ministral support | ✅ Ja | ✅ Ja |

**Aanbeveling:**
- Start met **Ollama** voor Ministral (simpeler)
- Gebruik **vLLM** of dedicated container voor Voxtral/STT
- Evalueer performance en switch indien nodig

---

## Orchestrator Architectuur (Open Vraag)

### Context

Dit is een thuisproject, geen enterprise applicatie. Doelen:
- **Leren** - nieuwe technologieën uitproberen
- **Modulair** - makkelijk onderdelen vervangen/upgraden
- **Overzichtelijk** - niet te complex, wel gestructureerd
- **Groeiend** - kan langzaam evolueren, geen einddatum

### Architectuur Opties

| Optie | Voordelen | Nadelen | Geschikt? |
|-------|-----------|---------|-----------|
| **Pure FastAPI** | Simpel, volledig in eigen hand, geen dependencies | Alles zelf bouwen | ✅ Start hier |
| **LangChain** | Veel kant-en-klare componenten, agents, chains | Veel abstractie, soms overkill, learning curve | 🤔 Later evalueren |
| **LangGraph** | Stateful agents, graph-based flows | Nieuwer, minder documentatie | 🤔 Later evalueren |
| **Custom Agents** | Precies wat je nodig hebt | Meer werk | Fase 5+ |

### Aanbevolen Aanpak

```
Fase 1-2: Pure FastAPI
├── Simpele request/response flow
├── Hardcoded pipeline: STT → LLM → TTS
├── State in-memory (dict of dataclass)
└── Focus op werkende basis

Fase 3-4: Evalueer complexiteit
├── Is LangChain/LangGraph nodig?
├── Agents voor autonome taken?
└── Betere state management nodig?

Fase 5+: Uitbreiden indien zinvol
├── Agent-based architecture
├── Complex conversation flows
└── Long-term memory
```

### Design Principes

| Principe | Toepassing |
|----------|------------|
| **OOP** | Classes voor services, encapsulation, inheritance waar zinvol |
| **SOLID** | Interfaces voor services, dependency injection, single responsibility |
| **KISS** | Start simpel, voeg complexiteit toe wanneer nodig |
| **DRY** | Herbruikbare componenten, geen copy-paste code |
| **Modulair** | Services via Docker, swappable implementations |
| **Pragmatisch** | Het hoeft niet "enterprise-grade" te zijn |

### Voorbeeld: Simpele Orchestrator (Fase 1)

```python
# services/orchestrator/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Simpele in-memory state
conversations: dict[str, list] = {}

class Request(BaseModel):
    audio: bytes
    image: bytes | None = None
    detections: list[dict] | None = None
    conversation_id: str

class Response(BaseModel):
    text: str
    function_calls: list[dict]

@app.post("/process")
async def process(request: Request) -> Response:
    # 1. STT
    transcript = await stt_service.transcribe(request.audio)

    # 2. Build context
    context = build_context(
        transcript=transcript,
        image=request.image,
        detections=request.detections,
        history=conversations.get(request.conversation_id, [])
    )

    # 3. LLM
    response = await llm_service.generate(context)

    # 4. Update history
    conversations[request.conversation_id].append(...)

    return Response(
        text=response.text,
        function_calls=response.function_calls
    )
```

Later kan dit evolueren naar agents, chains, of complexere flows - maar start simpel.

---

## Resources & Links

### STT (Speech-to-Text)
- [Voxtral Announcement](https://mistral.ai/news/voxtral) - Mistral's audio model
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Snelle Whisper implementatie
- [Whisper](https://github.com/openai/whisper) - OpenAI's originele model

### LLM
- [Mistral Models](https://mistral.ai/models)
- [Mistral Function Calling](https://docs.mistral.ai/capabilities/function_calling/)
- [Ollama](https://ollama.ai/) - Lokaal LLMs draaien

### TTS (Text-to-Speech)
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Open source, XTTS voor voice cloning
- [Piper TTS](https://github.com/rhasspy/piper) - Lightweight, Nederlandse stemmen
- [Bark](https://github.com/suno-ai/bark) - Expressieve TTS

### Object Detection
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - YOLOv8/v11
- [YOLO on Raspberry Pi](https://docs.ultralytics.com/guides/raspberry-pi/)

### Wake Word
- [Picovoice Porcupine](https://picovoice.ai/platform/porcupine/)
- [OpenWakeWord](https://github.com/dscripka/openWakeWord)

### PiCar-X
- [Official Docs](https://docs.sunfounder.com/projects/picar-x-v20/en/latest/)
- [picar-x-racer](https://github.com/KarimAziev/picar-x-racer) - YOLO integration
- [picar-cad](https://github.com/KarimAziev/picar-cad) - 3D printable parts

### Orchestration (Te Evalueren)
- [LangChain](https://python.langchain.com/) - LLM application framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Stateful agents

---

## Design Decisions

### Vastgesteld

| Vraag | Besluit | Reden |
|-------|---------|-------|
| Local of cloud? | **Local-first** | Kosten, privacy, geen rate limits, leerzamer |
| Cloud mogelijk? | **Ja, modulair** | Elke service swappable via interface |
| Containerized? | **Ja, Docker** | Isolatie, reproduceerbaarheid, makkelijk te deployen |
| Eerst desktop of Pi? | **Desktop first** | Sneller itereren, makkelijker debuggen |
| Wake word lokaal of cloud? | **Lokaal op Pi** | Latency, privacy, altijd beschikbaar |
| Aparte vision + LLM modellen? | **Nee, Ministral 8B/14B doet beide** | Simpeler, sneller, minder VRAM |
| Streaming vs batch audio? | **Batch met VAD** | Eenvoudiger, betrouwbaarder voor v1 |
| State management waar? | **Orchestrator** | Centraal punt, makkelijk debuggen |
| GPU verdeling? | **Primair RTX 4090** | 24GB VRAM, 5070 Ti als overflow (~12GB effectief) |

### Open Vragen (Te Bepalen via Experimenteren)

| Vraag | Opties | Criteria |
|-------|--------|----------|
| Welke STT? | Voxtral Mini vs faster-whisper | Accuracy, latency, function calling nodig? |
| Function calls in STT? | Ja (Voxtral) vs Nee (alleen LLM) | Voegt het waarde toe? Sentiment detectie nuttig? |
| TTS waar? | Desktop (primair) vs Pi (optimalisatie) | Kwaliteit vs latency trade-off |
| Welke TTS? | Coqui XTTS, Bark, Edge TTS, Piper | Nederlandse kwaliteit, natuurlijke klank |
| Object detection op Pi? | YOLO Nano/Small | Meerwaarde vs complexity |
| Orchestrator framework? | Pure FastAPI vs LangChain/LangGraph | Start simpel, evalueer later |

### Projectfilosofie

| Principe | Toelichting |
|----------|-------------|
| **Leren** | Doel is leren, niet perfectie |
| **Iteratief** | Start simpel, bouw uit |
| **Pragmatisch** | Geen enterprise-grade nodig |
| **Modulair** | Makkelijk onderdelen vervangen |
| **Geen einddatum** | Kan blijven groeien |

---

*Status: Concept / In Ontwikkeling*
*Laatst bijgewerkt: Januari 2026*
