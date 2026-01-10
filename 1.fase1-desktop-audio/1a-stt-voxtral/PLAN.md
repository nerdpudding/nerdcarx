# Subfase 1a: STT - Voxtral

**Status:** ✅ Docker Setup Complete - Eerste test succesvol!
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

### Stap 2: Docker Setup ✅

**Locatie:** [`docker/`](docker/) - bevat alle configuratie en test scripts.

- [x] NVIDIA Container Toolkit controleren
- [x] Custom Dockerfile met audio dependencies (librosa, soundfile)
- [x] Container starten: `docker compose build && docker compose up -d`
- [x] Health check: `curl http://localhost:8150/health`
- [x] Test transcriptie met audio sample

**Instructies:** Zie [`docker/README.md`](docker/README.md)

### Stap 3: Testen ✅ (basis)

- [ ] Test met Engels audio sample
- [x] Test met Nederlandse audio samples → "Hallo, oude gek" correct getranscribeerd!
- [ ] Test audio Q&A functionaliteit
- [x] VRAM gemeten: ~22.7GB (incl. KV cache), model zelf: 8.72GB
- [x] Latency: ~instant voor 3 sec audio

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

### Test Resultaten (2026-01-10)

**Setup:**
- Microfoon: Razer Seiren Mini (USB, mono)
- Opname: `arecord -D hw:5,0 -d 5 -f S16_LE -r 44100 -c 1 -t wav test.wav`

**Test 1: Nederlandse spraak**
- Input: "Hallo, oude gek" (3 sec)
- Output: `{"text":"Hallo, oude gek.","usage":{"type":"duration","seconds":3}}`
- Latency: ~instant
- Resultaat: ✅ Perfect

**Cruciale configuratie:**
1. Custom Dockerfile nodig met `vllm[audio]`, `librosa`, `soundfile`
2. Mistral format flags: `--tokenizer_mode mistral --config_format mistral --load_format mistral`
3. FP8 quantization werkt NIET met vLLM (zie models/README.md)

---

## Beslissingen

| Vraag | Besluit | Reden | Datum |
|-------|---------|-------|-------|
| Welk STT model? | **Voxtral Mini 3B** | Beste balans kwaliteit/VRAM, Nederlands ondersteund, function calling | 2026-01-10 |
| Welke quantization? | **Origineel (bf16)** | FP8 werkt niet met vLLM (zie models/README.md) | 2026-01-10 |
| Welke backend? | **vLLM** | Aanbevolen door Mistral, OpenAI-compatible API, goed voor real-time | 2026-01-10 |
| Faster-Whisper als fallback? | Nee (voorlopig) | Voxtral voldoet, function calling is meerwaarde | 2026-01-10 |
| GPU voor STT? | **GPU0 (RTX 4090)** | FP8 werkt niet, dus ~9.5GB nodig. Later uitzoeken of GPU1 (5070 Ti) kan. | 2026-01-10 |

---

## Gekozen Configuratie

```
Model:    mistralai/Voxtral-Mini-3B-2507 (origineel)
Backend:  vLLM nightly (0.14.0rc1) + custom Dockerfile
VRAM:     Model: 8.72 GB | KV Cache: 11.15 GB | Totaal: ~22.7 GB
GPU:      RTX 4090 (GPU0, primair)
API:      OpenAI-compatible via vLLM
Poort:    8150 (extern) → 8000 (intern)
```

> **Let op:** FP8 quantization werkt niet met vLLM.
> Zie `models/README.md` voor gedetailleerde uitleg van de issues.
>
> **VRAM optimalisatie:** Huidige setup gebruikt 90% GPU memory voor KV cache.
> Kan gereduceerd worden met `--gpu-memory-utilization 0.50` voor LLM naast STT.

### Waarom Voxtral Mini?

1. **Nederlands ondersteund** - één van de 8 officiële talen
2. **Function calling** - sentiment/urgentie detectie direct vanuit STT
3. **Noise robust** - beter dan Whisper in lawaaierige omgeving (robot motors)
4. **Audio understanding** - meer dan alleen transcriptie

### VRAM Overwegingen

Met het originele model (~9.5GB) blijft er ~14.5GB over op de RTX 4090 voor de LLM.
Dit is krap voor Ministral 8B in full precision, maar:
- Ministral 8B in INT4/GPTQ: ~5-6GB
- Ministral 8B in FP8: ~8GB

**TODO:** Later onderzoeken of Voxtral naar GPU1 (5070 Ti, ~16GB) kan worden verplaatst.
Mogelijke issues: Blackwell architectuur compatibiliteit, lagere performance.

### Volgende Stappen

1. [x] Meer info verzamelen over vLLM + Voxtral setup
2. [x] Docker configuratie gemaakt (incl. custom Dockerfile)
3. [x] Container draaien en testen
4. [x] Lokaal testen met Nederlandse audio samples
5. [x] VRAM en latency benchmarken

**Volgende fase:**
- VRAM optimaliseren (`--gpu-memory-utilization`) voor LLM naast STT
- Microphone streaming + VAD implementeren
- Integratie met Fase 1b (LLM)

---

[← Terug naar Fase 1](../FASE1-PLAN.md)
