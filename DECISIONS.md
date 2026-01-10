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

### D002: STT - Voxtral Mini 3B FP8 + vLLM

**Datum:** 2026-01-10
**Fase:** 1a
**Status:** Actief

**Besluit:**
| Aspect | Keuze |
|--------|-------|
| Model | `RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic` |
| Backend | vLLM >= 0.10.0 |
| VRAM | ~6 GB (model + overhead) |
| GPU | RTX 4090 |

**Rationale:**
1. Nederlands ondersteund (1 van 8 officiële talen)
2. Function calling mogelijk (sentiment/urgentie uit stem)
3. ~6GB VRAM, past naast LLM op RTX 4090
4. Noise robust (beter dan Whisper in lawaaierige omgeving)

**Alternatieven overwogen:**
- Faster-Whisper v3 Large - Afgewezen: geen function calling, minder noise robust

**Referentie:** [Research document](1.fase1-desktop-audio/1a-stt-voxtral/research/research.md)

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
| D002 | STT keuze | 2026-01-10 | Actief |

---

*Laatst bijgewerkt: 2026-01-10*
