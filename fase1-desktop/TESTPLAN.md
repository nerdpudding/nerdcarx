# Testplan: TTS Integratie

**Datum:** 2026-01-11
**Status:** ✅ Getest - Werkend met bekende issues

---

## Test Resultaten (2026-01-11)

### Timing Analyse

| Turn | Audio In | STT | LLM | TTS | Playback | Totaal |
|------|----------|-----|-----|-----|----------|--------|
| 1 | 2.7s | 144ms | 232ms | 0ms* | 0ms | 399ms |
| 2 | 2.8s | 142ms | 703ms | 4582ms | 8879ms | 14.3s |
| 3 | 15.4s | 753ms | 1233ms | 19610ms | 38823ms | 60.5s |
| 4 | 12.2s | 656ms | 9625ms | 12978ms | 25049ms | 48.3s |
| 5 | 3.5s | 223ms | 5038ms | 10075ms | 19697ms | 35.1s |
| 6 | 15.4s | 745ms | 1246ms | 10868ms | 20817ms | 33.7s |

*Turn 1: Lege response van LLM, geen TTS audio gegenereerd

### Gemiddelde Latency (excl. outliers)

| Component | Tijd | Percentage |
|-----------|------|------------|
| STT (Voxtral) | ~200-750ms | ~5% |
| LLM (Ministral 8B) | ~700-1300ms | ~10% |
| **TTS (Chatterbox)** | **5-20 sec** | **~40%** |
| Playback | ~2x TTS tijd | ~45% |

**Conclusie:** TTS is de grootste bottleneck.

### Bekende Issues

| Issue | Beschrijving | Prioriteit |
|-------|--------------|------------|
| TTS Latency | 5-20 seconden per response | Hoog |
| TTS Spreeksnelheid | Audio klinkt te snel | Medium |
| Emotion in tekst | LLM schrijft soms emotie in tekst ipv tool call | Laag |
| Lege response | Turn 1 had lege response, geen TTS | Laag |
| VRAM gebruik | ~18.3GB op 4090, lijkt toe te nemen | Onderzoeken |

### Observaties

1. **STT (Voxtral)**: Uitstekend! Zeer snel, ~150ms voor korte audio
2. **LLM (Ministral 8B)**: Acceptabel, soms spikes (Turn 4: 9.6s)
3. **TTS (Chatterbox)**: Bottleneck - lange generatietijd
4. **Vision (take_photo)**: Werkt, voegt ~3-4s toe aan LLM tijd
5. **Emotion tool calls**: Werkt meestal, soms in tekst verwerkt

### VRAM Notitie

- GPU0 (RTX 4090): ~18.3GB in gebruik
- Lijkt geleidelijk toe te nemen tijdens gesprek
- TTS zou geen context moeten bijhouden - mogelijk memory leak?
- **TODO:** Monitoren en onderzoeken

---

## Test Procedure

### Vereisten

| Service | Port | Conda Env |
|---------|------|-----------|
| Voxtral STT | 8150 | (Docker) |
| Ollama LLM | 11434 | - |
| Orchestrator | 8200 | nerdcarx-vad |
| TTS Service | 8250 | nerdcarx-tts |

### Stap 1: Start Services

```bash
# Terminal 1: Voxtral (als nog niet draait)
cd fase1-desktop/stt-voxtral/docker
docker compose up -d

# Terminal 2: TTS
conda activate nerdcarx-tts
cd fase1-desktop/tts
uvicorn tts_service:app --port 8250

# Terminal 3: Orchestrator
conda activate nerdcarx-vad
cd fase1-desktop/orchestrator
uvicorn main:app --port 8200 --reload

# Terminal 4: VAD Conversation
conda activate nerdcarx-vad
cd fase1-desktop/vad-desktop
python vad_conversation.py
```

### Stap 2: Verificatie

```bash
# Health checks
curl http://localhost:8150/health  # Voxtral
curl http://localhost:8200/health  # Orchestrator
curl http://localhost:8200/status  # Alle services
curl http://localhost:8250/health  # TTS
```

### Stap 3: End-to-End Test

**VAD output toont nu timing per component:**
```
📝 Transcriberen... ✅ (142ms)
👤 Jij: Hallo
🔄 Processing (LLM+TTS)... ✅ (LLM: 703ms | TTS: 4582ms)
🔧 [TOOL CALLS] ...
🎭 [EMOTIE] neutral 😐 (behouden)
🤖 NerdCarX: ...
🔊 Afspelen... ✅ (8879ms)
⏱️  [TIMING] STT: 142ms | LLM: 703ms | TTS: 4582ms | Playback: 8879ms | TOTAAL: 14327ms
```

### Test Scenario's

| Test | Input | Verwacht | Status |
|------|-------|----------|--------|
| Begroeting | "Hallo" | Response + audio | ✅ |
| Emotie trigger | "Je bent geweldig!" | show_emotion tool call | ✅* |
| Vision | "Wat zie je?" | take_photo + beschrijving | ✅ |
| Lange input | 15+ sec spraak | Proportionele timing | ✅ |

*Emotie werkt meestal via tool call, soms in tekst verwerkt

---

## Stoppen

```bash
# VAD: Ctrl+C of zeg "stop nu het gesprek"
# Orchestrator: Ctrl+C
# TTS: Ctrl+C
# Voxtral: docker compose down
```

---

## Volgende Stappen (Optimalisatie)

1. **TTS Latency onderzoeken**
   - Streaming TTS (per zin genereren)?
   - Andere TTS modellen vergelijken?
   - GPU optimalisatie?

2. **TTS Snelheid aanpassen**
   - `cfg_weight` parameter verhogen voor langzamer
   - Speech rate parameter zoeken in Chatterbox

3. **VRAM monitoren**
   - nvidia-smi tijdens gesprek
   - Memory leak identificeren

4. **Emotion tool call verbeteren**
   - System prompt aanscherpen
   - Groter model proberen (14B)?

---

## Config Referentie

```yaml
# config.yml
tts:
  url: "http://localhost:8250"
  enabled: true
  language: "nl"
  emotion_mapping:
    neutral:   { exaggeration: 0.5, cfg_weight: 0.5 }
    happy:     { exaggeration: 0.7, cfg_weight: 0.4 }
    # cfg_weight lager = sneller, hoger = langzamer
```

---

*Laatst bijgewerkt: 2026-01-11 (eerste volledige test)*
