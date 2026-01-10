# Fase 1: Desktop Audio Pipeline

**Status:** Eerste sprint - basis flow werkt
**Doel:** Werkende spraak-naar-spraak loop op desktop (Docker komt later)

## Huidige Stand (2026-01-11)

```
[Desktop Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral LLM] → response
                                              ↓
                                    + Vision (foto meesturen)
                                    + Function calling (emoties)
```

**Wat werkt:**
- STT via Voxtral (Docker op GPU1)
- LLM via Ministral 14B (Ollama op GPU0)
- Orchestrator (lokaal in conda)
- VAD hands-free gesprekken
- Vision (foto bij elke request)
- Function calling (show_emotion tool)

**Wat nog moet:**
- TTS (volgende stap)
- Prompt tuning (model gedrag te speels)
- Dockerizen (later, als base stabiel is)

---

## Subfases

| Sub | Onderdeel | Status | Beschrijving |
|-----|-----------|--------|--------------|
| 1a | [STT (Voxtral)](./1a-stt-voxtral/) | ✅ Werkt | Docker container op GPU1 |
| 1b | LLM (Ministral) | ⚠️ Experimenteel | Werkt, maar prompt tuning nodig |
| 1c | TTS | 🔜 Volgende | Onderzoek opties morgen |
| 1d | [Orchestrator](./1d-orchestrator/) | ⚠️ Basis werkt | Lokaal in conda, vision + tools |
| 1e | GPU Allocatie | ✅ Bepaald | GPU0: LLM, GPU1: STT |
| 1f | Integratie/Docker | Later | Na basis stabiel is |
| 1g | [VAD Desktop](./1g-vad-desktop/) | ✅ Werkt | Hands-free gesprekken |

---

## Volgende Stappen

1. **TTS onderzoek** (morgen)
   - Opties: Coqui XTTS, Piper, Bark, etc.
   - Criteria: Nederlands, latency, kwaliteit

2. **Prompt tuning** (doorlopend)
   - Ministral's "Le Chat" persoonlijkheid temmen
   - Zakelijker gedrag zonder grappen/emoji's

3. **Dockerizen** (later)
   - Orchestrator in container
   - docker-compose voor hele stack

4. **Hardware integratie** (na hardware binnenkomt)
   - Pi 5 verbinding
   - OLED display
   - Motors/servo's

---

## Quick Start (huidige setup)

```bash
# Terminal 1: Voxtral STT (GPU1)
cd 1a-stt-voxtral/docker
docker compose up -d

# Terminal 2: Ollama LLM (GPU0)
docker run -d --gpus device=0 -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama-nerdcarx -e OLLAMA_KV_CACHE_TYPE=q8_0 ollama/ollama
docker exec ollama-nerdcarx ollama pull ministral-3:14b

# Terminal 3: Orchestrator
conda activate nerdcarx-vad
cd 1d-orchestrator
uvicorn main:app --port 8200 --reload

# Terminal 4: VAD Conversation
conda activate nerdcarx-vad
cd 1g-vad-desktop
python vad_conversation.py
```

---

## Voortgang

| Datum | Update |
|-------|--------|
| 2026-01-10 | Fase 1 opgebroken in subfases |
| 2026-01-10 | 1a: Voxtral STT werkt in Docker |
| 2026-01-10 | 1g: VAD desktop scripts gemaakt |
| 2026-01-11 | 1d: Orchestrator met function calling |
| 2026-01-11 | 1d: Vision support toegevoegd |
| 2026-01-11 | Volledige chain werkt (STT→LLM→response) |

---

[← Terug naar README](../README.md)
