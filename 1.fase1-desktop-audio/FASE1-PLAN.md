# Fase 1: Desktop Audio Pipeline

**Status:** In Voorbereiding
**Doel:** Werkende spraak-naar-spraak loop, volledig in Docker op desktop

## Overzicht

```
[Desktop Mic] → [STT Container] → [LLM Container] → [TTS Container] → [Desktop Speaker]
```

Deze fase bouwt de complete audio pipeline als Docker services op de desktop, zonder enige hardware afhankelijkheid.

---

## Subfases

Fase 1 is opgebroken in losse onderdelen die elk apart ontwikkeld en getest kunnen worden.

| Sub | Onderdeel | Status | Beschrijving |
|-----|-----------|--------|--------------|
| 1a | [STT (Voxtral)](./1a-stt-voxtral/) | ✅ **Compleet** | Voxtral Mini + vLLM - transcriptie en chat werkt |
| 1b | LLM (Ministral) | Klaar | Al werkend via Ollama - later system prompt |
| 1c | TTS | Gepland | Onderzoek opties, testen Nederlands, Pi-geschiktheid |
| 1d | Orchestrator | Gepland | FastAPI, STT→LLM→TTS flow, conversation state |
| 1e | GPU Allocatie | Gepland | Na benchmarks bepalen |
| 1f | Integratie | Gepland | Alles aan elkaar, end-to-end test |
| 1g | [VAD Desktop](./1g-vad-desktop/) | **Nieuw** | Silero VAD voor hands-free testing |

---

## Subfase Details

### 1a. STT - Voxtral

**Doel:** Voxtral werkend krijgen in Docker, performance en VRAM benchmarken

**Locatie:** `1a-stt-voxtral/`

**Kernvragen:**
- Welk Voxtral model? (Mini 3B vs Medium)
- vLLM als backend - hoe configureren?
- Hoeveel VRAM nodig?
- Welke latency haalbaar?

> **Opmerking:** Function calling hoort bij de LLM (Ministral), niet bij STT. Zie [D003](../DECISIONS.md#d003-function-calling---ministral-llm-niet-voxtral-stt).

---

### 1b. LLM - Ministral

**Status:** Al werkend via Ollama

**Later te doen:**
- Custom modelfile met robot system prompt
- Function calling schema toevoegen (zie Fase 2)
- Tools definieren (show_emotion, move_robot, etc.)

> **Opmerking:** Function calling gebeurt hier, niet bij STT. Ministral 3B/8B ondersteunt
> dit officieel. Zie [D003](../DECISIONS.md#d003-function-calling---ministral-llm-niet-voxtral-stt).

---

### 1c. TTS - Onderzoek

**Doel:** Beste TTS vinden voor Nederlands met lage latency

**Criteria:**
- Goede Nederlandse uitspraak
- Lage latency
- Potentieel op Pi draaibaar (nice to have)
- Offline capable

**Te onderzoeken opties:**
- Desktop: Coqui XTTS, Bark, Edge TTS, en andere
- Lightweight: Piper, espeak-ng, en andere
- Nieuwere opties die mogelijk beter zijn

**Let op:** Piper is NIET automatisch de keuze - "kan houterig klinken"

---

### 1d. Orchestrator

**Doel:** FastAPI service die alles aan elkaar knoopt

**Componenten:**
- `/process` endpoint (audio in → response uit)
- STT service client
- LLM service client
- TTS service client (optioneel in fase 1)
- Conversation history management
- Error handling

**Architectuur:** Pure FastAPI, geen LangChain/LangGraph (voor nu)

---

### 1e. GPU Allocatie

**Beschikbaar:**
- RTX 4090 (24GB VRAM) - primair
- RTX 5070 Ti (~12GB effectief) - overflow

**Te bepalen na benchmarks:**
- Kan alles op 4090?
- Welke service naar 5070 Ti indien nodig?
- Concurrent gebruik mogelijk?

---

### 1f. Integratie

**Doel:** Alles werkend als geheel

**Test criteria:**
- End-to-end: spraak in → spraak uit
- Latency < 2 seconden
- Conversation history werkt
- Elke service apart testbaar

---

### 1g. VAD Desktop

**Doel:** Hands-free testing van audio pipeline met Voice Activity Detection

**Locatie:** `1g-vad-desktop/`

**Aanpak:**
- Silero VAD voor spraak detectie
- Conda environment met Python 3.14, pip voor packages
- Simpel script dat luistert, detecteert, en naar Voxtral stuurt

**Let op:** Dit is voor desktop testing. VAD oplossing voor Pi wordt later apart onderzocht.

---

## Mapstructuur

```
1.fase1-desktop-audio/
├── FASE1-PLAN.md              # Dit bestand
├── 1a-stt-voxtral/            # ✅ Subfase 1a - Compleet
│   ├── PLAN.md                # Onderzoek en implementatieplan
│   ├── docker/                # Docker configuratie
│   └── test-audio/            # Test scripts en samples
├── 1g-vad-desktop/            # Subfase 1g - In ontwikkeling
│   └── PLAN.md                # VAD implementatieplan
├── 1c-tts/                    # Subfase 1c (later)
├── 1d-orchestrator/           # Subfase 1d (later)
└── docker-compose.yml         # Gezamenlijke compose (later)
```

---

## Voortgang

| Datum | Update |
|-------|--------|
| 2026-01-10 | Fase 1 opgebroken in subfases, start met 1a |
| 2026-01-10 | **1a: STT keuze gemaakt** - Voxtral Mini 3B + vLLM |
| 2026-01-10 | **1a: Docker setup klaar** - Container config in `1a-stt-voxtral/docker/` |
| 2026-01-10 | **1a: Tests compleet** - Transcriptie en chat werkt |
| 2026-01-10 | **1g: VAD Desktop** - Plan gemaakt voor hands-free testing met Silero VAD |

---

[← Terug naar README](../README.md)
