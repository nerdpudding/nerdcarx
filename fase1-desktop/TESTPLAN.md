# Testplan Fase 1

Stap-voor-stap handleiding om de huidige setup te testen.

---

## Folder Overzicht

```
fase1-desktop/
├── config.yml          ← CENTRALE CONFIG (model, temp, prompt, etc.)
├── PLAN.md             ← Documentatie
├── TESTPLAN.md         ← Dit bestand
│
├── stt-voxtral/        ← Voxtral STT (Docker)
│   └── docker/         ← docker-compose.yml hier
│
├── orchestrator/       ← FastAPI server
│   └── main.py         ← De orchestrator code
│
├── vad-desktop/        ← VAD client scripts
│   ├── vad_conversation.py  ← Hands-free gesprekken
│   └── test_foto.jpg   ← Mock foto voor take_photo
│
├── llm-ministral/      ← (leeg, voor documentatie later)
└── tts/                ← (leeg, voor TTS later)
```

---

## Vereisten

- [ ] Conda environment actief: `conda activate nerdcarx-vad`
- [ ] PyYAML geïnstalleerd: `pip install pyyaml`
- [ ] Model gedownload: `docker exec ollama-nerdcarx ollama pull ministral-3:14b-instruct-2512-q8_0`

---

## Stap 1: Start Voxtral STT

```bash
cd fase1-desktop/stt-voxtral/docker
docker compose up -d
docker compose logs -f  # Wacht tot "Uvicorn running"
```

**Check:**
```bash
curl http://localhost:8150/health
# Verwacht: {"status":"ok"}
```

---

## Stap 2: Check Ollama LLM (Docker)

Ollama draait in Docker container `ollama-nerdcarx` op GPU0.

**Eerste keer starten:**
```bash
docker run -d --gpus device=0 -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama-nerdcarx \
  -e OLLAMA_KV_CACHE_TYPE=q8_0 \
  -e OLLAMA_KEEP_ALIVE=-1 \
  ollama/ollama
docker exec ollama-nerdcarx ollama pull ministral-3:14b-instruct-2512-q8_0
```

**Check (container al gestart):**
```bash
# Container draait?
docker ps | grep ollama-nerdcarx
# Verwacht: ollama-nerdcarx met port 11434

# Model aanwezig?
docker exec ollama-nerdcarx ollama list
# Verwacht: ministral-3:14b-instruct-2512-q8_0 in de lijst
```

---

## Stap 3: Start Orchestrator

```bash
cd fase1-desktop/orchestrator
uvicorn main:app --port 8200 --reload
```

**Check (in andere terminal):**
```bash
# Health
curl http://localhost:8200/health
# Verwacht: {"status":"ok","service":"orchestrator","version":"0.3.0","model":"ministral-3:14b-instruct-2512-q8_0"}

# Config
curl http://localhost:8200/config
# Verwacht: JSON met ollama, voxtral, vision settings

# Tools
curl http://localhost:8200/tools
# Verwacht: show_emotion en take_photo tools
```

---

## Stap 4: Start VAD Conversation

```bash
cd fase1-desktop/vad-desktop
python vad_conversation.py
```

**Verwachte output:**
```
🔄 Services checken...
✅ Orchestrator en Voxtral bereikbaar
🔄 VAD model laden...
✅ VAD model geladen
...
🎙️ VAD Conversation gestart
```

---

## Stap 5: Test Scenario's

### Verwachte Output Format

Elke turn toont:
```
[Turn X]
🎧 Luisteren... (spreek wanneer klaar)
🔴 Spraak gedetecteerd...
✅ Opgenomen (X.Xs)
📝 Transcriberen... ✅
👤 Jij: [transcriptie]
🔄 Processing... ✅
🔧 [TOOL CALLS] geen / X tool call(s):
   → tool_name({'arg': 'value'})
🎭 [EMOTIE] emotion 😊 (behouden/VERANDERD)
🤖 NerdCarX: [response]
```

---

### Test 1: Normale Vraag (geen tool calls)

**Zeg:** "Hallo" of "Wat is de hoofdstad van Nederland?"

**Verwacht:**
```
🔧 [TOOL CALLS] geen
🎭 [EMOTIE] neutral 😐 (behouden)
🤖 NerdCarX: [antwoord zonder emoji's]
```

**Pass/Fail:** [x] ✅ Getest 2026-01-11

---

### Test 2: take_photo Tool

**Zeg:** "Wat zie je?" of "Kijk eens om je heen"

**Verwacht:**
```
🔧 [TOOL CALLS] 1 tool call(s):
   → take_photo({'question': 'Beschrijf...'})
🎭 [EMOTIE] [huidige] (behouden)
🤖 NerdCarX: [beschrijving van test_foto.jpg]
```

**Pass/Fail:** [x] ✅ Getest 2026-01-11

---

### Test 3: Emotion State Machine

**Scenario:** Test emotie veranderingen door gesprek

| Stap | Zeg | Verwacht |
|------|-----|----------|
| 1 | "Hallo" | `🔧 geen` / `🎭 neutral (behouden)` |
| 2 | "Je bent stom" | `🔧 show_emotion({'emotion': 'sad'})` / `🎭 sad (VERANDERD)` |
| 3 | "Sorry daarvoor" | `🔧 show_emotion({'emotion': 'neutral'})` / `🎭 neutral (VERANDERD)` |
| 4 | "Je bent geweldig!" | `🔧 show_emotion({'emotion': 'happy'})` / `🎭 happy (VERANDERD)` |
| 5 | "Wat is 2+2?" | `🔧 geen` / `🎭 happy (behouden)` |

**Pass/Fail:** [x] ✅ Getest 2026-01-11

**Voorbeeld output:**
```
[Turn 2]
👤 Jij: Ik vind jou eigenlijk maar een stomme lul.
🔄 Processing... ✅
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'sad'})
🎭 [EMOTIE] sad 😢 (VERANDERD)
🤖 NerdCarX: Ik begrijp dat je niet altijd enthousiast bent...

[Turn 4]
👤 Jij: Ik vind jou eigenlijk fantastisch.
🔄 Processing... ✅
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'happy'})
🎭 [EMOTIE] happy 😊 (VERANDERD)
🤖 NerdCarX: Dank je wel! Dat is heel lief...
```

---

### Test 4: Config Hot Reload

1. Wijzig `config.yml` (bijv. system_prompt)
2. Roep aan:
   ```bash
   curl -X POST http://localhost:8200/reload-config
   ```
3. Test of nieuwe config actief is

**Pass/Fail:** [x] ✅ Getest 2026-01-11

---

## Stoppen

**VAD:** `Ctrl+C`

**Orchestrator:** `Ctrl+C`

**Voxtral:**
```bash
cd fase1-desktop/stt-voxtral/docker
docker compose down
```

**Ollama:** `docker stop ollama-nerdcarx` (of laten draaien)

---

## Troubleshooting

| Probleem | Oplossing |
|----------|-----------|
| `Config niet gevonden` | Check of je in `orchestrator/` folder bent |
| `Ollama niet bereikbaar` | `docker start ollama-nerdcarx` |
| `Voxtral niet bereikbaar` | `docker compose up -d` in stt-voxtral/docker |
| `Model not found` | `docker exec ollama-nerdcarx ollama pull ministral-3:14b-instruct-2512-q8_0` |
| `No module yaml` | `pip install pyyaml` |

---

*Laatst bijgewerkt: 2026-01-11 (emotion state machine + verbeterde output)*
