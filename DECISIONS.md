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

**Bevindingen (2026-01-11):**
- Q8 quantization is duidelijk beter dan Q4 voor response kwaliteit
- VRAM gebruik: ~20GB op GPU0 (4090), past met speling
- Vision latency: ~5-10s door dubbele LLM call (tool detection + image analyse)
- Cold start na container restart kan eerste request vertragen

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

### D007: Emotion State Machine

**Datum:** 2026-01-11
**Fase:** 1
**Status:** ✅ Geïmplementeerd en getest

**Besluit:**
Emoties als persistente state in de orchestrator. De robot simuleert emoties die beïnvloed worden door de gebruiker.

**Kenmerken:**
- In-memory state per conversation_id
- Auto-reset naar neutral na 5 minuten inactiviteit
- Huidige emotie meegegeven aan LLM in system prompt
- Tool call alleen bij VERANDERING van emotie
- Verbeterde VAD output met duidelijke status indicators

**Problemen en oplossingen:**

1. **Model schreef tool calls als tekst** (`show_emotion[ARGS]{...}`)
   - Oplossing: Fallback parsing in orchestrator met regex
   - Functie `parse_text_tool_calls()` haalt Mistral format uit tekst

2. **Model maakte geen emotie tool calls bij negatieve input**
   - Oorzaak: Vage prompt instructies + model safety training
   - Oplossing: Expliciete prompt dat robot EIGEN emotie simuleert

3. **Output onduidelijk over tool calls**
   - Oplossing: Verbeterde VAD output met ✅ checkmarks en tool call details

**VAD Output voorbeeld (werkend):**
```
[Turn 1]
🎧 Luisteren... (spreek wanneer klaar)
🔴 Spraak gedetecteerd...
✅ Opgenomen (2.1s)
📝 Transcriberen... ✅
👤 Jij: Hallo.
🔄 Processing... ✅
🔧 [TOOL CALLS] geen
🎭 [EMOTIE] neutral 😐 (behouden)
🤖 NerdCarX: Hoi! Ik ben NerdCarX...

[Turn 2]
👤 Jij: Ik vind jou eigenlijk maar een stomme lul.
🔄 Processing... ✅
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'sad'})
🎭 [EMOTIE] sad 😢 (VERANDERD)
🤖 NerdCarX: Ik begrijp dat je niet altijd enthousiast bent...

[Turn 3]
👤 Jij: Sorry, dat meende ik niet.
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'neutral'})
🎭 [EMOTIE] neutral 😐 (VERANDERD)

[Turn 4]
👤 Jij: Ik vind jou eigenlijk fantastisch.
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'happy'})
🎭 [EMOTIE] happy 😊 (VERANDERD)
```

**Response format:**
```json
{
  "emotion": {
    "current": "happy",
    "changed": true,
    "auto_reset": false,
    "had_tool_call": true
  }
}
```

**Bestanden gewijzigd:**
- `orchestrator/main.py` - State management + text-based tool call parsing
- `vad-desktop/vad_conversation.py` - Verbeterde debug output
- `config.yml` - Emotie prompt instructies

**Referentie:** [Plan](docs/plans/emotion_state_machine_2026-01-11.md)

---

## Open vragen

> Vragen die nog beantwoord moeten worden tijdens implementatie.

| ID | Vraag | Verwacht in fase | Status |
|----|-------|------------------|--------|
| Q001 | Welke TTS? (Coqui, Piper, Bark, Kokoro, etc.) | 1 | **Volgende stap** |
| Q002 | TTS op desktop of Pi? | 1 | Open |
| Q003 | Object detection op Pi? (YOLO) | Later | Open |
| Q004 | Orchestrator framework? | 1d | ✅ Pure FastAPI |
| Q005 | Context management strategy? (sliding window, truncation) | 2 | Open - intermittent 500 errors bij lange gesprekken met vision |

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
| D007 | Emotion State Machine | 2026-01-11 | ✅ Geïmplementeerd |

---

*Laatst bijgewerkt: 2026-01-11 (emotion state machine volledig werkend)*
