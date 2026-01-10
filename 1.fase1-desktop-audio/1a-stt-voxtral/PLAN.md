# Subfase 1a: STT - Voxtral

**Status:** Docker Setup
**Doel:** Voxtral werkend krijgen in Docker, los van andere services

---

## Onderzoeksvragen

### Model Keuze

| Vraag | Te Onderzoeken |
|-------|----------------|
| Welke Voxtral modellen bestaan er? | Mini (3B), Medium, andere? |
| Welk model past bij onze use case? | Balans tussen kwaliteit en VRAM/snelheid |
| Wat zijn de VRAM requirements? | Per model variant |
| Ondersteunt Voxtral Nederlands? | Accuracy testen |

### Backend / Serving

| Vraag | Te Onderzoeken |
|-------|----------------|
| Is vLLM de beste optie? | Performance, ease of setup |
| Alternatieven voor vLLM? | HuggingFace Transformers, andere? |
| Docker image beschikbaar? | Bestaande images of zelf bouwen |
| API formaat? | OpenAI compatible? Custom? |

### Performance

| Vraag | Te Onderzoeken |
|-------|----------------|
| Latency voor typische utterance? | ~3-5 seconden audio |
| VRAM gebruik? | Idle vs inference |
| Throughput? | Niet kritisch, maar goed om te weten |
| GPU keuze? | 4090 vs 5070 Ti |

### Extra Capabilities

| Vraag | Te Onderzoeken |
|-------|----------------|
| Function calling vanuit STT? | Voxtral ondersteunt dit - nuttig? |
| Sentiment detectie in stem? | Kan het, en willen we het? |
| Timestamps/word-level? | Voor latere sync met OLED |

---

## Implementatiestappen

### Stap 1: Research ✅

- [x] Mistral documentatie lezen over Voxtral
- [x] HuggingFace model cards bekijken
- [x] vLLM documentatie voor audio modellen
- [x] VRAM requirements verzamelen

**Output:** Notities in `research/` map

### Stap 2: Docker Setup (huidige stap)

**Locatie:** [`docker/`](docker/) - bevat alle configuratie en test scripts.

- [ ] NVIDIA Container Toolkit controleren
- [ ] Container starten: `docker compose up -d`
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Test transcriptie met audio sample

**Instructies:** Zie [`docker/README.md`](docker/README.md)

### Stap 3: Testen

- [ ] Test met Engels audio sample (Obama)
- [ ] Test met Nederlandse audio samples
- [ ] Test audio Q&A functionaliteit
- [ ] VRAM meten (`nvidia-smi`)
- [ ] Latency meten

### Stap 4: Microphone + VAD (later)

- [ ] Microphone input implementeren
- [ ] Voice Activity Detection (VAD)
- [ ] Real-time opname en transcriptie

---

## Resources

### Officieel

- [Voxtral Announcement](https://mistral.ai/news/voxtral)
- [Mistral Docs](https://docs.mistral.ai/)
- [vLLM Documentation](https://docs.vllm.ai/)

### Te Zoeken

- HuggingFace model page voor Voxtral
- vLLM audio model support
- Community Docker images
- Benchmark resultaten van anderen

---

## Notities

*Voeg hier notities toe tijdens onderzoek en implementatie*

---

## Beslissingen

| Vraag | Besluit | Reden | Datum |
|-------|---------|-------|-------|
| Welk STT model? | **Voxtral Mini 3B** | Beste balans kwaliteit/VRAM, Nederlands ondersteund, function calling | 2026-01-10 |
| Welke quantization? | **FP8** (RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic) | ~4.75GB VRAM, goede kwaliteit, past ruim op RTX 4090 | 2026-01-10 |
| Welke backend? | **vLLM** | Aanbevolen door Mistral, OpenAI-compatible API, goed voor real-time | 2026-01-10 |
| Faster-Whisper als fallback? | Nee (voorlopig) | Voxtral voldoet, function calling is meerwaarde | 2026-01-10 |

---

## Gekozen Configuratie

```
Model:    RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic
Backend:  vLLM (>= 0.10.0)
VRAM:     ~6 GB totaal (model + overhead)
GPU:      RTX 4090 (primair)
API:      OpenAI-compatible via vLLM
```

### Waarom Voxtral Mini FP8?

1. **Nederlands ondersteund** - één van de 8 officiële talen
2. **Function calling** - sentiment/urgentie detectie direct vanuit STT
3. **VRAM efficiënt** - ~6GB, laat ~18GB over voor LLM op zelfde GPU
4. **Noise robust** - beter dan Whisper in lawaaierige omgeving (robot motors)
5. **Audio understanding** - meer dan alleen transcriptie

### Volgende Stappen

1. [x] Meer info verzamelen over vLLM + Voxtral setup
2. [x] Docker configuratie gemaakt
3. [ ] Container draaien en testen
4. [ ] Lokaal testen met Nederlandse audio samples
5. [ ] VRAM en latency benchmarken

**Nu te doen:** Ga naar `docker/` en volg de instructies in `README.md`.

---

[← Terug naar Fase 1](../FASE1-PLAN.md)
