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

**Referentie:** Zie fase1-desktop/PLAN.md

---

### D008: TTS - Chatterbox Multilingual

**Datum:** 2026-01-11
**Fase:** 1
**Status:** ❌ Vervangen door D009 (te traag: 5-20s per response)

**Besluit:**
Chatterbox Multilingual voor Text-to-Speech met Nederlandse spraaksynthese.

| Aspect | Keuze |
|--------|-------|
| Model | `ResembleAI/chatterbox` (500M parameters) |
| Taal | Nederlands (native support, language_id="nl") |
| Emotie | `exaggeration` parameter (0.25-2.0) |
| Latency | ~1-2s per zin op RTX 4090 |
| Licentie | MIT |
| Conda env | `nerdcarx-tts` (aparte env, torch==2.6.0) |

**Rationale:**
1. ElevenLabs-kwaliteit (won 63% in blind tests)
2. Nederlandse taal native ondersteund
3. Emotie controle via `exaggeration` parameter - past bij emotion state machine
4. Zero-shot voice cloning mogelijk voor later
5. MIT licentie, geen restricties

**Alternatieven onderzocht:**
| Model | Reden afgewezen |
|-------|-----------------|
| Kokoro | Geen Nederlands |
| Fish Speech | Licentie restricties |
| Coqui XTTS | Niet meer actief ontwikkeld |
| Piper | Minder expressief |

**Implementatie:**
- TTS service op port 8250 (`tts_service.py`)
- Orchestrator roept TTS aan met schone tekst (geen function calls)
- Emotie → exaggeration mapping in config.yml
- Response bevat `audio_base64` veld

**Referentie:** [Plan](archive/old-plans/tts_chatterbox_2026-01-11.md)

**Test Resultaten (2026-01-11):**
| Component | Latency | Opmerking |
|-----------|---------|-----------|
| STT | 150-750ms | Uitstekend |
| LLM | 700-1300ms | Acceptabel |
| **TTS** | **5-20 sec** | **Bottleneck** |
| Playback | ~2x TTS | Correlatie met audio lengte |

**Bekende issues:**
- TTS latency hoog (5-20 sec per response)
- Audio klinkt te snel
- VRAM ~18.3GB, lijkt toe te nemen (memory leak?)

---

### D009: TTS - Fish Audio S1-mini (vervangt D008)

**Datum:** 2026-01-11
**Fase:** 1
**Status:** ✅ Geïmplementeerd

**Besluit:**
Fish Audio S1-mini vervangt Chatterbox als TTS vanwege betere latency.

| Aspect | Keuze |
|--------|-------|
| Model | `fishaudio/openaudio-s1-mini` (0.5B parameters) |
| Backend | Docker container met GPU |
| Taal | Nederlands via reference audio |
| Latency | ~1.2s per zin (vs 5-20s Chatterbox) |
| Port | 8250 |

**Rationale:**
1. ~4x sneller dan Chatterbox (1.2s vs 5-20s)
2. #1 op TTS-Arena2 benchmark
3. Voice cloning via reference audio
4. Actief ontwikkeld (MIT licentie)

**Alternatieven getest:**
| Model | Latency | Nederlands | Reden afgewezen |
|-------|---------|------------|-----------------|
| Chatterbox | 5-20s | ✅ Goed | Te traag |
| VibeVoice | 1-2s | ❌ Belgisch accent | Kwaliteit |
| Coqui XTTS-v2 | - | - | Project dood, Docker onbeschikbaar |
| Piper | <100ms | ✅ | Backup optie (minder expressief) |

**Setup:**
```bash
# Model downloaden (via git lfs)
cd original_fish-speech-REFERENCE
git lfs install
git clone https://huggingface.co/fishaudio/openaudio-s1-mini checkpoints/openaudio-s1-mini

# Docker starten
docker run --gpus device=0 --name fish-tts \
    -v $(pwd)/checkpoints:/app/checkpoints \
    -p 8250:8080 --entrypoint uv \
    fishaudio/fish-speech \
    run tools/api_server.py --listen 0.0.0.0:8080 --compile
```

**Reference Audio:**
- Bron: ElevenLabs Nederlandse vrouwenstem
- ID: `dutch2`
- Bestanden: `fase1-desktop/tts/fishaudio/elevenreference/`

**Parameters (geteste configuraties):**
| Configuratie | temperature | top_p | Omschrijving |
|--------------|-------------|-------|--------------|
| very_consistent | 0.3 | 0.6 | Iets natuurlijker, kleine variatie |
| **ultra_consistent** | **0.2** | **0.5** | **GEKOZEN - beste Nederlandse uitspraak** |

**API Voorbeeld:**
```bash
curl -X POST http://localhost:8250/v1/tts \
    -H "Content-Type: application/json" \
    -d '{"text": "Hallo!", "reference_id": "dutch2", "temperature": 0.2, "top_p": 0.5, "format": "wav"}' \
    --output test.wav
```

**Referentie:** [Fish Audio README](fase1-desktop/tts/fishaudio/README.md)

---

## Open vragen

> Vragen die nog beantwoord moeten worden tijdens implementatie.

| ID | Vraag | Verwacht in fase | Status |
|----|-------|------------------|--------|
| Q001 | Welke TTS? (Coqui, Piper, Bark, Kokoro, etc.) | 1 | ✅ Fish Audio S1-mini (D009) |
| Q002 | TTS op desktop of Pi? | 1 | ✅ Desktop (aparte conda env) |
| Q003 | Object detection op Pi? (YOLO) | Later | Open |
| Q004 | Orchestrator framework? | 1d | ✅ Pure FastAPI |
| Q005 | Context management strategy? (sliding window, truncation) | 2 | Open - intermittent 500 errors bij lange gesprekken met vision |
| Q006 | TTS latency optimalisatie? (streaming, chunking, ander model) | 2 | ✅ Fish Audio ~1.2s (D009) |
| Q007 | TTS spreeksnelheid aanpassen? | 2 | Open - audio klinkt te snel |
| Q008 | VRAM memory leak? | 2 | Open - ~18.3GB, lijkt toe te nemen |

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
| D008 | TTS Chatterbox | 2026-01-11 | ❌ Vervangen door D009 |
| D009 | TTS Fish Audio S1-mini | 2026-01-11 | ✅ Geïmplementeerd |

---

*Laatst bijgewerkt: 2026-01-11 (TTS Fish Audio vervangt Chatterbox)*
