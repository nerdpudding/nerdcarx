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

### Test 1: Normale Vraag

**Zeg:** "Hoe laat is het?" of "Wat is de hoofdstad van Nederland?"

**Verwacht:**
- Zakelijk antwoord
- GEEN emoji's in de response
- GEEN grappen of humor

**Pass/Fail:** [ ]

---

### Test 2: take_photo Tool

**Zeg:** "Wat zie je voor je?" of "Beschrijf je omgeving"

**Verwacht in terminal:**
```
📷 [FOTO] Analyseren: ...
🤖 NerdCarX: [beschrijving van test_foto.jpg]
```

**Pass/Fail:** [ ]

---

### Test 3: show_emotion Tool

**Zeg:** "Ik ben heel blij vandaag!" of "Dit is frustrerend"

**Verwacht in terminal:**
```
🎭 [EMOTIE] happy 😊
```
(of andere relevante emotie)

**Pass/Fail:** [ ]

---

### Test 4: Config Hot Reload

1. Wijzig `config.yml` (bijv. system_prompt)
2. Roep aan:
   ```bash
   curl -X POST http://localhost:8200/reload-config
   ```
3. Test of nieuwe config actief is

**Pass/Fail:** [ ]

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

*Laatst bijgewerkt: 2026-01-11*
