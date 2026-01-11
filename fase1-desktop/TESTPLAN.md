# Testplan: End-to-End Pipeline

**Datum:** 2026-01-11
**Status:** ✅ Getest - Werkend

---

## Test Resultaten (2026-01-11)

### Huidige Performance (Fish Audio S1-mini)

| Component | Latency | Opmerking |
|-----------|---------|-----------|
| STT (Voxtral) | 150-750ms | Uitstekend |
| LLM (Ministral 8B) | 700-1300ms | Acceptabel |
| TTS (Fish Audio) | ~1.2s | Goed (was 5-20s met Chatterbox) |
| Vision | +3-4s | Dubbele LLM call |

### Bekende Issues

| Issue | Beschrijving | Prioriteit |
|-------|--------------|------------|
| TTS accent | Klinkt soms Engelserig via orchestrator | Medium |
| STT taal | Voxtral negeert soms `language: 'nl'` | Laag |
| Playback interrupt | Geen mogelijkheid om af te breken | Wens |

### Observaties

1. **STT (Voxtral)**: Uitstekend! Zeer snel, ~150ms voor korte audio
2. **LLM (Ministral 8B)**: Acceptabel, soms spikes bij lange context
3. **TTS (Fish Audio)**: ~4x sneller dan Chatterbox
4. **Vision (take_photo)**: Werkt, voegt ~3-4s toe aan LLM tijd
5. **Emotion tool calls**: Werkt meestal, soms in tekst verwerkt

---

## Test Procedure

### Vereisten

| Service | Port | Setup |
|---------|------|-------|
| Voxtral STT | 8150 | Docker (GPU1) |
| Ollama LLM | 11434 | Docker/native (GPU0) |
| Fish Audio TTS | 8250 | Docker (GPU0) |
| Orchestrator | 8200 | Conda nerdcarx-vad |

### Stap 1: Start Services

```bash
# Terminal 1: Voxtral (als nog niet draait)
cd fase1-desktop/stt-voxtral/docker
docker compose up -d

# Terminal 2: Fish Audio TTS (Docker)
cd original_fish-speech-REFERENCE
docker run -d --gpus device=0 --name fish-tts \
    -v $(pwd)/checkpoints:/app/checkpoints \
    -v $(pwd)/references:/app/references \
    -p 8250:8080 --entrypoint uv \
    fishaudio/fish-speech \
    run tools/api_server.py --listen 0.0.0.0:8080 --compile

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
curl http://localhost:8150/health     # Voxtral
curl http://localhost:8200/health     # Orchestrator
curl http://localhost:8200/status     # Alle services
curl http://localhost:8250/v1/health  # Fish Audio TTS
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
# Fish Audio TTS: docker stop fish-tts
# Voxtral: docker compose down
```

---

## Open Punten

1. **TTS accent via orchestrator**
   - Parameters vergelijken: standalone test vs orchestrator
   - Kortere zinnen genereren in LLM prompt?

2. **Emotion tool call verbeteren**
   - System prompt aanscherpen
   - Groter model proberen (14B)?

3. **Playback interrupt**
   - Mogelijkheid om audio af te breken tijdens afspelen

---

## Config Referentie

```yaml
# config.yml
tts:  # Fish Audio S1-mini
  url: "http://localhost:8250"
  enabled: true
  reference_id: "dutch2"
  temperature: 0.2   # ultra_consistent
  top_p: 0.5
  format: "wav"
```

---

*Laatst bijgewerkt: 2026-01-11 (Fish Audio S1-mini)*
