# Subfase 1a: STT - Voxtral

**Status:** Onderzoek
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

### Stap 1: Research

- [ ] Mistral documentatie lezen over Voxtral
- [ ] HuggingFace model cards bekijken
- [ ] vLLM documentatie voor audio modellen
- [ ] Community examples/tutorials zoeken
- [ ] VRAM requirements verzamelen

**Output:** Notities in `research/` map

### Stap 2: Basis Opzet

- [ ] Model downloaden (HuggingFace)
- [ ] vLLM installatie (lokaal eerst, dan Docker)
- [ ] Eerste test: audio file → transcriptie
- [ ] API endpoint werkend

### Stap 3: Docker Container

- [ ] Dockerfile schrijven
- [ ] GPU passthrough configureren
- [ ] Health check endpoint
- [ ] Volume mounts voor model cache

### Stap 4: Benchmarks

- [ ] VRAM meten (idle + inference)
- [ ] Latency meten met test audio files
- [ ] Nederlandse audio samples testen
- [ ] Resultaten documenteren

### Stap 5: API Design

- [ ] Input formaat bepalen (audio blob, file, stream?)
- [ ] Output formaat (tekst, timestamps, confidence?)
- [ ] Error handling
- [ ] OpenAI-compatible API? (voor swappability)

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
| - | - | - | - |

---

[← Terug naar Fase 1](../FASE1-PLAN.md)
