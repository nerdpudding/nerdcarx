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

**Referentie:** [Research document](1.fase1-desktop-audio/1a-stt-voxtral/research/research.md)

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

## Open vragen

> Vragen die nog beantwoord moeten worden tijdens implementatie.

| ID | Vraag | Verwacht in fase |
|----|-------|------------------|
| Q001 | Welke TTS? (Coqui, Piper, Bark, etc.) | 1c |
| Q002 | TTS op desktop of Pi? | 1c |
| Q003 | Object detection op Pi? (YOLO) | 4b |
| Q004 | Orchestrator framework? (Pure FastAPI vs LangChain) | 1d |

---

## Beslissingen index

| ID | Onderwerp | Datum | Status |
|----|-----------|-------|--------|
| D001 | Project aanpak | 2026-01-10 | Actief |
| D002 | STT keuze | 2026-01-10 | Actief (bijgewerkt) |
| D003 | Function calling locatie | 2026-01-10 | Actief |

---

*Laatst bijgewerkt: 2026-01-10*
