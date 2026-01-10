# Fase 1: Desktop Audio Pipeline

**Status:** Gepland
**Doel:** Werkende spraak-naar-spraak loop, volledig in Docker op desktop

## Overzicht

```
[Desktop Mic] → [STT Container] → [LLM Container] → [TTS Container] → [Desktop Speaker]
```

Deze fase bouwt de complete audio pipeline als Docker services op de desktop, zonder enige hardware afhankelijkheid.

## Taken

### Setup
- [ ] Docker Compose configuratie opzetten
- [ ] Netwerk en volumes configureren
- [ ] Development environment documenteren

### STT Service
- [ ] Container voor STT opzetten
- [ ] Keuze maken: Voxtral Mini vs faster-whisper
- [ ] API endpoint implementeren
- [ ] Testen met audio samples

### LLM Service
- [ ] Ollama container opzetten
- [ ] Ministral 8B/14B model downloaden
- [ ] System prompt configureren
- [ ] API endpoint testen

### TTS Service
- [ ] Container voor TTS opzetten
- [ ] Experimenteren met opties (Coqui XTTS, Bark, Piper)
- [ ] Nederlandse stem selecteren/configureren
- [ ] API endpoint implementeren

### Orchestrator
- [ ] FastAPI project opzetten
- [ ] Request/Response modellen definiëren
- [ ] STT → LLM → TTS flow implementeren
- [ ] Conversation history bijhouden
- [ ] Error handling

### Testen
- [ ] CLI interface voor handmatig testen
- [ ] End-to-end test: spraak in → spraak uit
- [ ] Latency meten en documenteren

## Architectuur

```yaml
# docker-compose.yml structure
services:
  orchestrator:
    build: ./services/orchestrator
    ports: ["8000:8000"]
    depends_on: [stt, llm, tts]

  stt:
    # Voxtral of faster-whisper
    # GPU: RTX 4090

  llm:
    image: ollama/ollama
    # Ministral 8B/14B
    # GPU: RTX 4090

  tts:
    # Coqui XTTS, Bark, of Piper
    # GPU of CPU afhankelijk van keuze
```

## Success Criteria

| Criterium | Target |
|-----------|--------|
| End-to-end werkt | Spraak → antwoord |
| Latency | < 2 seconden |
| Conversation history | Meerdere beurten |
| Services testbaar | Elke API apart |
| Nederlandse TTS | Verstaanbaar |

## Open Vragen

1. **STT keuze:** Voxtral Mini (function calling) vs faster-whisper (lichter)?
2. **TTS keuze:** Welke klinkt het beste in Nederlands?
3. **GPU allocatie:** Alles op 4090 of verdelen over GPUs?

## Voortgang

| Datum | Update |
|-------|--------|
| - | Fase nog niet gestart |

## Notities

*Voeg hier notities, learnings en beslissingen toe tijdens de implementatie*

---

[← Terug naar README](../README.md) | [Volgende: Fase 2 →](../2.fase2-function-calling/FASE2-PLAN.md)
