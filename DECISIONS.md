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

**Referentie:** [Research document](archive/old-docs/stt-research/research.md)

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

**Referentie:** Zie fase1-desktop/README.md

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

**Datum:** 2026-01-11, bijgewerkt 2026-01-16
**Fase:** 1
**Status:** ✅ Geïmplementeerd + Verbeterd

**Besluit:**
Fish Audio S1-mini vervangt Chatterbox als TTS vanwege betere latency.

| Aspect | Keuze |
|--------|-------|
| Model | `fishaudio/openaudio-s1-mini` (0.5B parameters) |
| Backend | Docker container met GPU |
| Taal | Nederlands via 30s ElevenLabs reference audio |
| Latency | ~600ms per zin (streaming) / ~1.2s (batch) |
| Port | 8250 |

**Verbeteringen (2026-01-16):**
- **Pseudo-streaming**: TTS per zin via SSE voor ~3x snellere perceived latency
- **Text normalisatie**: acroniemen → NL fonetiek ("API" → "aa-pee-ie")
- **Langere reference**: 30s ElevenLabs audio met alle emoties en probleemwoorden
- **Playback interrupt**: Spatiebalk onderbreekt audio in streaming mode

**Rationale:**
1. ~4x sneller dan Chatterbox (streaming nog sneller perceived)
2. #1 op TTS-Arena2 benchmark
3. Voice cloning via reference audio
4. Actief ontwikkeld (MIT licentie)

**Alternatieven getest:**
| Model | Latency | Nederlands | Reden afgewezen |
|-------|---------|------------|-----------------|
| Chatterbox | 5-20s | ✅ Goed | Te traag |
| VibeVoice | 1-2s | ❌ Belgisch accent | Slechte Kwaliteit |
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
    -v $(pwd)/references:/app/references \
    -p 8250:8080 --entrypoint uv \
    fishaudio/fish-speech \
    run tools/api_server.py --listen 0.0.0.0:8080 --compile
```

**Reference Audio:**
- Bron: ElevenLabs Nederlandse vrouwenstem
- ID: `dutch2`
- Locatie: `original_fish-speech-REFERENCE/references/dutch2/reference.mp3` (30s)
- Bevat: alle emoties, probleemwoorden, moeilijke klanken (sch, ui, eu, ij, g/ch)

**Parameters (finale configuratie):**
| Configuratie | temperature | top_p | Omschrijving |
|--------------|-------------|-------|--------------|
| **Huidig** | **0.5** | **0.6** | **Expressief met 30s reference** |
| ultra_consistent (oud) | 0.2 | 0.5 | Was te monotoon |

**Streaming:**
```yaml
# config.yml
tts:
  streaming: true  # Per-zin TTS via SSE
```

**API Voorbeeld:**
```bash
curl -X POST http://localhost:8250/v1/tts \
    -H "Content-Type: application/json" \
    -d '{"text": "Hallo!", "reference_id": "dutch2", "temperature": 0.5, "top_p": 0.6, "format": "wav"}' \
    --output test.wav
```

**Bekende beperkingen:**
- Sommige woorden klinken nog Engels (Fish Audio limitatie)
- Vraagintonatie niet altijd correct (model limitatie)

**Referentie:** [Fish Audio README](fase1-desktop/tts/fishaudio/README.md)

---

### D010: Camera Module 3 (vervangt OV5647)

**Datum:** 2026-01-16
**Fase:** 3
**Status:** Gepland

**Besluit:**
Upgrade van OV5647 (kit camera) naar Camera Module 3 (IMX708).

| Aspect | OV5647 (huidig) | Camera Module 3 |
|--------|-----------------|-----------------|
| Sensor | OmniVision 5MP | Sony IMX708 12MP |
| Autofocus | Nee | Ja |
| HDR | Nee | Ja (stacked) |
| Low-light | Matig | Beter |

**Rationale:**
1. Autofocus essentieel voor variabele afstanden (navigatie, close-up)
2. HDR verbetert robuustheid bij wisselende lichtomstandigheden
3. Hogere resolutie voor betere YOLO/SLAM feature detection
4. Past bij hybride perceptie architectuur (lokaal + remote)

**Alternatieven overwogen:**
| Camera | Reden afgewezen |
|--------|-----------------|
| AI Camera (IMX500) | Model lock-in, duurder, minder flexibel voor hybride aanpak |
| Arducam alternatieven | Minder documentatie, compatibility risico |
| Huidige OV5647 houden | Geen autofocus, slechte low-light, beperkt voor SLAM |

**Referentie:** [4-Laags Perceptie Architectuur](docs/feature-proposals/4-layer-perception-architecture.md)

---

### D011: 4-Laags Perceptie Architectuur

**Datum:** 2026-01-16
**Fase:** 3-4
**Status:** Gepland

**Besluit:**
Implementeer een 4-laags architectuur die verantwoordelijkheden scheidt naar waar ze logisch thuishoren:

| Laag | Doel | Locatie | Latency | Waarom |
|------|------|---------|---------|--------|
| **0 Safety** | Obstacle avoidance | Pi lokaal | <50ms | Moet werken zonder WiFi |
| **1 Navigatie** | SLAM, route planning | Pi lokaal | Real-time | Control loops voorspelbaar |
| **2 Perceptie** | Pose, VLM, heavy AI | Desktop GPU | ~200ms OK | GPU vrijheid |
| **3 Conversatie** | STT→LLM→TTS | Desktop | Niet kritisch | Al geïmplementeerd |

**Rationale:**
1. Safety-kritische functies moeten blijven werken bij WiFi problemen
2. Desktop GPU (RTX 4090/5070 Ti) biedt modelflexibiliteit voor zware taken
3. ~200ms latency naar desktop is acceptabel voor niet-safety perceptie
4. Schaalt naar SLAM en geavanceerde navigatie zonder architectuur wijziging

**Dual Vision Pad:**
```
Camera Module 3
      │
      ├──► [Pi] YOLO nano → Safety (Laag 0)
      │
      └──► [Stream] → Desktop → Pose/VLM (Laag 2)
```

**Impact op bestaande plannen:**
- Fase 3: Camera Module 3, YOLO safety, streaming setup
- Fase 4: SLAM, pose detectie, room discovery features

**Referentie:** [4-Laags Perceptie Architectuur](docs/feature-proposals/4-layer-perception-architecture.md)

---

### D012: Hardware Uitbreiding (ToF, LEDs, OLED, I2C Hub)

**Datum:** 2026-01-16
**Fase:** 3
**Status:** Besteld

**Besluit:**
Definitieve hardware configuratie voor NerdCarX. LiDAR is out of scope (te duur, te veel stroom).

**Nieuwe componenten:**

| Component | Doel | Interface |
|-----------|------|-----------|
| TCA9548A I2C Hub | Meerdere I2C devices met zelfde adres | I2C @ 0x70 |
| 2x VL53L0X ToF | Zijwaartse afstandsmeting (links/rechts) | I2C via hub @ 0x29 |
| 2x Grove LED (wit) | Indicator/waarschuwingslichten | Digital D0, D1 |
| OLED WPI438 (SSD1306) | Status display, emoties | I2C @ 0x3C |

**Rationale:**
1. ToF sensoren: Nauwkeuriger dan ultrasonic voor korte afstanden, goed voor zijwaartse obstacle detection
2. I2C Hub: Nodig omdat beide VL53L0X hetzelfde vaste adres hebben (0x29)
3. LEDs: Visuele feedback voor obstacle warning, kan ook als koplampen
4. OLED: Emotie display (vervangt desktop simulator), status info

**Wiring:**
- LEDs op D0 (GPIO17) en D1 (GPIO4) - enige vrije digital pins
- OLED direct op I2C bus (naast hub)
- ToF sensoren via hub kanalen CH0 en CH1

**Referentie:** [Hardware Reference](docs/hardware/HARDWARE-REFERENCE.md)

---

### D013: Fase 2 Architectuur - Modulaire Orchestrator + WebSocket

**Datum:** 2026-01-16
**Fase:** 2
**Status:** ✅ Geïmplementeerd

**Besluit:**
Volledige refactor van orchestrator naar modulaire structuur met Docker Compose.

**Architectuur keuzes:**

| Aspect | Keuze | Rationale |
|--------|-------|-----------|
| **Service abstractie** | Protocol pattern (niet ABC) | Lichter, duck typing, makkelijk te mocken |
| **Config** | Dataclasses + env var expansion | Type-safe, ${VAR:-default} voor Docker |
| **WebSocket** | Native FastAPI WebSocket | Pi ↔ Desktop real-time communicatie |
| **Docker** | Multi-service compose | Voxtral + TTS + Orchestrator in één stack |

**Folder structuur:**
```
orchestrator/app/
├── main.py           # FastAPI entry (slim)
├── config.py         # Config loading + env vars
├── routes/           # health, chat, websocket
├── services/         # STT, LLM, TTS, Tools (Protocol-based)
├── models/           # Pydantic schemas, emotion, conversation
├── websocket/        # Protocol, manager, handlers
└── utils/            # Text normalization
```

**WebSocket Protocol:**
- Pi → Desktop: `audio_process`, `wake_word`, `heartbeat`, `sensor_update`
- Desktop → Pi: `response`, `audio_chunk`, `function_call`, `error`

**Docker Compose services:**
| Service | Port | GPU | Notes |
|---------|------|-----|-------|
| ollama | 11434 | GPU0 | Shared volume met andere ollama container |
| voxtral | 8150 | GPU1 | STT via vLLM |
| tts | 8250 | GPU0 | Fish Audio S1-mini |
| orchestrator | 8200 | CPU | FastAPI |

**Volumes:**
- `ollama` (external) - Gedeelde volume, kan naast andere ollama container bestaan
- `tts-cache` - Compile cache voor snellere TTS restarts

**Update 2026-01-16:** Ollama nu IN de stack voor eenvoudiger beheer (`docker compose up -d` start alles).

**Referentie:** [fase2-refactor/README.md](fase2-refactor/README.md)

---

### D014: Wake Word - OpenWakeWord v0.4.0

**Datum:** 2026-01-16
**Fase:** 3
**Status:** ✅ Geïmplementeerd

**Besluit:**
OpenWakeWord v0.4.0 met `hey_jarvis` pre-trained model voor wake word detectie op Pi.

| Aspect | Keuze |
|--------|-------|
| Library | OpenWakeWord v0.4.0 |
| Model | `hey_jarvis` (pre-trained) |
| Runtime | ONNX (niet TFLite) |
| Threshold | 0.5 |
| CPU usage | ~2-5% |

**KRITIEK:** Gebruik versie **0.4.0**, NIET 0.6.0!
- v0.6.0 faalt: `tflite-runtime` heeft geen wheel voor Python 3.13 ARM64
- v0.4.0 werkt: gebruikt ONNX Runtime

**Rationale:**
1. 100% open source, geen account nodig (vs Porcupine)
2. Pre-trained models beschikbaar
3. Laag CPU gebruik (~2-5%)
4. Ingebouwde Speex noise suppression
5. Werkt met ONNX Runtime op ARM64 Pi

**Alternatieven overwogen:**
| Optie | Reden afgewezen |
|-------|-----------------|
| Picovoice Porcupine | Account vereist, niet 100% open source |
| Snowboy | Discontinued |
| Mycroft Precise | Minder accuraat |

**Toekomst (low priority):**
- Custom "hey nerd" model trainen via Google Colab
- Community modellen: https://github.com/fwartner/home-assistant-wakewords-collection

**Test resultaten:** Scores 0.85-1.00 bij duidelijke "hey jarvis"

**Referentie:** [fase3-pi/PLAN.md](fase3-pi/PLAN.md)

---

### D015: Pi VAD - Silero VAD v4 via ONNX Runtime

**Datum:** 2026-01-16
**Fase:** 3
**Status:** ✅ Geïmplementeerd

**Besluit:**
Silero VAD v4 via ONNX Runtime voor Voice Activity Detection op Pi.

| Aspect | Keuze |
|--------|-------|
| Model | Silero VAD v4 |
| Runtime | ONNX Runtime (niet PyTorch) |
| Chunk size | 480 samples (30ms @ 16kHz) |
| State | h/c tensors (shape 2,1,64) |

**KRITIEK:** Gebruik Silero VAD **v4 model**, NIET nieuwere versies!
- v4: inputs `h`/`c` (shape 2,1,64) - WERKT
- Nieuwere: input `state` (shape 128) - WERKT NIET correct
- Download URL: `https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.onnx`

**Rationale:**
1. ML-based, zeer accuraat voor speech vs noise
2. ONNX Runtime lichter dan PyTorch op ARM Pi
3. Bewezen in fase1-desktop
4. Geen dependency hell (PyTorch op ARM = problematisch)

**Alternatieven overwogen:**
| Optie | Reden afgewezen |
|-------|-----------------|
| PyTorch Silero | Dependency hell op ARM Pi |
| WebRTC VAD | Minder accuraat |
| speech_recognition energy-based | Minder robuust in noisy environments |

**Referentie:** [fase3-pi/PLAN.md](fase3-pi/PLAN.md)

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
| D010 | Camera Module 3 | 2026-01-16 | Gepland |
| D011 | 4-Laags Perceptie Architectuur | 2026-01-16 | Gepland |
| D012 | Hardware Uitbreiding (ToF, LEDs, OLED) | 2026-01-16 | Besteld |
| D013 | Fase 2 Architectuur (Modulair + WebSocket) | 2026-01-16 | ✅ Geïmplementeerd |
| D014 | Wake Word - OpenWakeWord v0.4.0 | 2026-01-16 | ✅ Geïmplementeerd |
| D015 | Pi VAD - Silero VAD v4 ONNX | 2026-01-16 | ✅ Geïmplementeerd |

---

*Laatst bijgewerkt: 2026-01-17 (Fase 3a compleet - Pi audio pipeline werkend)*
