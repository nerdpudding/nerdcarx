# NerdCarX - Beslissingen Log

> **Dit is de centrale plek voor alle projectbeslissingen.**
> Andere documenten verwijzen hiernaar. Dit voorkomt verwarring over wat actueel is.

---

## Hoe dit document werkt

- Elke beslissing krijgt een **ID** (bv. `D001`)
- Beslissingen worden **chronologisch** toegevoegd (nieuwste onderaan)
- **Nooit verwijderen** - als een beslissing herzien wordt, voeg een nieuwe toe met referentie
- Linkt naar research/context waar relevant

---

## Beslissingen

### D001: Project aanpak - Local-first, Desktop-first

**Datum:** 2026-01-10
**Fase:** 0 (Concept)
**Status:** Actief

**Besluit:**
- Alles draait lokaal (geen cloud APIs)
- Ontwikkeling start op desktop, later naar Pi
- Docker containers voor alle services

**Rationale:** Kosten, privacy, geen rate limits, sneller itereren, leerzamer.

**Referentie:** [Origineel concept](archive/0.concept/picar-x-ai-companion-concept.md)

---

### D002: STT - Voxtral Mini 3B + vLLM

**Datum:** 2026-01-10
**Fase:** 1a
**Status:** Actief (bijgewerkt)

**Besluit:**
| Aspect | Keuze |
|--------|-------|
| Model | `mistralai/Voxtral-Mini-3B-2507` (bf16 origineel) |
| Backend | vLLM >= 0.10.0 |
| VRAM | ~15 GB (op GPU1) |
| GPU | RTX 5070 Ti (GPU1) |

**Rationale:**
1. Nederlands ondersteund (1 van 8 officiële talen)
2. ~15GB VRAM op GPU1, laat GPU0 (4090) vrij voor LLM
3. Noise robust (beter dan Whisper in lawaaierige omgeving)
4. Audio understanding (Q&A, samenvatting)

**Alternatieven overwogen:**
- Faster-Whisper v3 Large - Afgewezen: minder noise robust
- FP8 quantization - Afgewezen: werkt niet met vLLM

**Referentie:** [Research document](fase1-desktop/stt-voxtral/research/research.md)

---

### D003: Function Calling - Ministral LLM, niet Voxtral STT

**Datum:** 2026-01-10
**Fase:** 1a/2
**Status:** Actief

**Besluit:**
Function calling wordt afgehandeld door de **Ministral LLM** (Fase 2), niet door Voxtral STT.

**Rationale:**
1. Voxtral function calling bleek niet betrouwbaar via vLLM deployment
2. Initiële tests leken te werken, maar waren prompt-gebaseerd (model genereerde toevallig juiste tekst)
3. Ministral 3B/8B ondersteunt function calling officieel en betrouwbaar
4. Architectureel logischer: STT doet spraak-naar-tekst, LLM doet reasoning + acties

**Flow:**
```
[Audio] → [Voxtral STT] → tekst → [Ministral LLM] → response + function calls
                                         ↓
                                   [TTS] + [Robot acties]
```

**Impact:**
- Voxtral scope beperkt tot transcriptie en audio Q&A
- Function calling volledig in Fase 2 (Ministral LLM)
- Geen wijziging in eindresultaat, alleen betere scheiding van verantwoordelijkheden

---

### D004: Orchestrator - Pure FastAPI (voorlopig)

**Datum:** 2026-01-11
**Fase:** 1d
**Status:** Actief

**Besluit:**
Orchestrator is pure FastAPI, geen LangChain/LangGraph. Beantwoordt Q004.

**Rationale:** Simpeler, sneller te ontwikkelen, volledige controle.

**Let op:** Dit is een eerste implementatie. Draait lokaal in conda, Docker komt later.

---

### D005: LLM - Ministral 14B Instruct Q8

**Datum:** 2026-01-11
**Fase:** 1
**Status:** Actief

**Besluit:**
Ministral 14B Instruct Q8 via Ollama voor LLM + Vision + Function calling.

**Huidige setup:** `ministral-3:14b-instruct-2512-q8_0` op GPU0 (RTX 4090)

**Officiële parameters:**
| Parameter | Waarde | Reden |
|-----------|--------|-------|
| Temperature | 0.15 | Officieel - hoger = hallucinaties |
| Top_p | 1.0 | NIET verlagen |
| Repeat_penalty | 1.0 | Officieel |

**Aandachtspunten:**
- Model heeft sterke ingebakken persoonlijkheid ("Le Chat")
- Zakelijke system prompt in centrale `config.yml`
- Vision werkt via `take_photo` function call

---

### D006: Fase Herindeling

**Datum:** 2026-01-11
**Fase:** 1
**Status:** Actief

**Besluit:**
Fases herzien van feature-based naar milestone-based:

| Fase | Oud | Nieuw |
|------|-----|-------|
| 1 | Desktop Audio Pipeline | Desktop Compleet (STT + LLM + Vision + Tools + TTS) |
| 2 | Function Calling | Refactor + Docker |
| 3 | Pi Integratie | Pi Integratie (ongewijzigd) |
| 4 | Vision | ~~Verwijderd~~ (al in Fase 1) |
| 5 | Autonomie | → Fase 4: Autonomie |

**Rationale:**
1. Function calling en Vision waren al in Fase 1 geïmplementeerd als "verkenning"
2. Feature-based fases creëerden overlap en verwarring
3. Milestone-based is duidelijker: eerst alles werkend, dan opschonen, dan hardware

**Folder wijzigingen:**
- `1.fase1-desktop-audio/` → `fase1-desktop/`
- `2.fase2-function-calling/` → `archive/old-fase-plans/`
- `3.fase3-pi-integratie/` → `fase3-pi/`
- `4.fase4-vision/` → `archive/old-fase-plans/`
- `5.fase5-autonomie/` → `fase4-autonomie/`

**Subfolder prefixes verwijderd:**
- `1a-stt-voxtral/` → `stt-voxtral/`
- `1d-orchestrator/` → `orchestrator/`
- `1g-vad-desktop/` → `vad-desktop/`

---

## Open vragen

> Vragen die nog beantwoord moeten worden tijdens implementatie.

| ID | Vraag | Verwacht in fase | Status |
|----|-------|------------------|--------|
| Q001 | Welke TTS? (Coqui, Piper, Bark, etc.) | 1c | Open |
| Q002 | TTS op desktop of Pi? | 1c | Open |
| Q003 | Object detection op Pi? (YOLO) | Later | Open |
| Q004 | Orchestrator framework? | 1d | ✅ Pure FastAPI |

---

## Beslissingen index

| ID | Onderwerp | Datum | Status |
|----|-----------|-------|--------|
| D001 | Project aanpak | 2026-01-10 | Actief |
| D002 | STT keuze | 2026-01-10 | Actief |
| D003 | Function calling locatie | 2026-01-10 | Actief |
| D004 | Orchestrator framework | 2026-01-11 | Actief |
| D005 | LLM keuze | 2026-01-11 | Actief |
| D006 | Fase herindeling | 2026-01-11 | Actief |

---

*Laatst bijgewerkt: 2026-01-11*
