# Detailed Model Comparison: Voxtral Mini vs Faster-Whisper v3 Large

## Overview

This comparison helps you choose between two speech recognition approaches: Voxtral Mini (a multimodal LLM with audio understanding) and Faster-Whisper (an optimized pure transcription engine).

## Specifications Comparison

| Feature | Voxtral Mini (FP8) | Voxtral Mini (bf16) | Faster-Whisper v3 Large |
|---------|-------------------|---------------------|------------------------|
| **Model Size** | 3B parameters | 3B parameters | 1550M parameters |
| **Base VRAM** | ~4.75 GB | ~9.5 GB | ~4.5 GB (FP16) |
| **Quantized VRAM** | N/A (already quantized) | ~2.5 GB (Q4_K_M) | ~3 GB (INT8) |
| **Context Window** | 32,000 tokens | 32,000 tokens | ~30 seconds |
| **Supported Languages** | 8 (EN, ES, FR, PT, HI, DE, NL, IT) | 8 languages | 50+ languages |
| **Audio Duration** | 30 min transcription / 40 min understanding | Same | Unlimited (segmented) |
| **Specialization** | Audio understanding + LLM | Same | Pure transcription |
| **License** | Apache 2.0 | Apache 2.0 | MIT |

## Capabilities Comparison

| Capability | Voxtral Mini 3B | Faster-Whisper v3 Large |
|------------|-----------------|------------------------|
| Transcription | ✅ Yes | ✅ Yes |
| Q&A from Audio | ✅ Yes | ❌ No |
| Summarization | ✅ Yes | ❌ No |
| Function Calling | ❌ Not reliable via vLLM | ❌ No |
| Translation | ✅ Yes (8 langs) | ✅ Yes (50+ langs) |
| Speaker Diarization | Implicit via context | Requires separate model |
| Long-form Audio | Up to 40 min native | Unlimited via VAD chunking |

> **Note on Function Calling:** While Mistral documentation mentions function calling support,
> testing revealed this is not reliable when deployed via vLLM. Function calling should be
> handled by the main LLM (Ministral) which receives the transcribed text as input.

## Benchmark Performance

### Word Error Rate (WER) - Lower is Better

**Important note**: Mistral's headline benchmarks are primarily for Voxtral Small (24B). Voxtral Mini (3B) performs slightly below Small but still outperforms Whisper large-v3 on most tasks.

| Benchmark | Voxtral Small 24B | Voxtral Mini 3B | Whisper large-v3 |
|-----------|-------------------|-----------------|------------------|
| LibriSpeech Clean | 1.2% | ~1.5-2.0%* | 1.9% |
| CHiME-4 (noisy) | 6.4% | ~7-8%* | 9.7% |
| FLEURS (multilingual) | SOTA | Competitive | Baseline |

*Estimated based on model scaling; Mini consistently beats Whisper but trails Small.

### Speed Comparison

Voxtral Mini offers significantly faster inference than Whisper for equivalent audio:
- Voxtral via vLLM: Optimized for concurrent requests, high throughput
- Faster-Whisper: ~4x faster than original Whisper, ~52s for 13 min audio (FP16)

## Platform Recommendations

### vLLM (Recommended for Voxtral Mini)

**VRAM Usage**: ~4.75GB (FP8) + ~1GB overhead = ~6GB total

**Installation**:
```bash
pip install vllm>=0.10.0
pip install mistral_common>=1.8.1
```

**Launch Command**:
```bash
vllm serve RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic \
  --tokenizer_mode mistral \
  --config_format mistral \
  --load_format mistral \
  --max-model-len 4864
```

**Best For**: Real-time applications, multi-user scenarios, API endpoints, audio understanding tasks.

### llama.cpp (Alternative for Voxtral Mini)

**VRAM Usage**: ~2.5GB (Q4_K_M) + minimal overhead

**Requirements**: 
- Build from source with CUDA support
- Separate `mmproj` file for multimodal support

**Best For**: Edge deployment, single-user applications, resource-constrained environments.

### Faster-Whisper / CTranslate2 (For Whisper)

**VRAM Usage**: 
- FP16: ~4.5 GB
- INT8: ~3 GB

**Installation**:
```bash
pip install faster-whisper
```

**Usage**:
```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="float16")
# Or for lower VRAM: compute_type="int8_float16"

segments, info = model.transcribe("audio.mp3", beam_size=5)
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

**Best For**: Pure transcription pipelines, multilingual requirements, existing Whisper workflows.

## VRAM Requirements by GPU

### RTX 4090 (24GB)

| Configuration | VRAM Used | Available for Context/Batching |
|---------------|-----------|-------------------------------|
| Voxtral Mini FP8 + vLLM | ~6 GB | ~18 GB |
| Voxtral Mini Q4_K_M | ~3.5 GB | ~20.5 GB |
| Faster-Whisper FP16 | ~4.5 GB | ~19.5 GB |
| Faster-Whisper INT8 | ~3 GB | ~21 GB |

### RTX 5070 Ti (16GB)

| Configuration | VRAM Used | Available |
|---------------|-----------|-----------|
| Voxtral Mini FP8 + vLLM | ~6 GB | ~10 GB |
| Voxtral Mini Q4_K_M | ~3.5 GB | ~12.5 GB |
| Faster-Whisper FP16 | ~4.5 GB | ~11.5 GB |
| Faster-Whisper INT8 | ~3 GB | ~13 GB |

### Hybrid Deployment (Both Models)

Running both models simultaneously:
- Voxtral Mini FP8 (~5 GB) + Faster-Whisper INT8 (~3 GB) = ~8 GB total
- Fits comfortably on RTX 5070 Ti with headroom for batching

**Note**: Multi-GPU tensor parallelism across different GPU architectures (e.g., RTX 4090 + 5070 Ti) is not recommended. vLLM tensor parallelism works best with identical GPUs connected via NVLink or high-bandwidth PCIe.

## Voxtral Mini Strengths

**Audio Intelligence**: Unlike traditional STT, Voxtral maintains semantic understanding across long audio:

- **Direct Q&A**: Ask questions about audio content without separate transcription + LLM pipeline
- **Contextual Summarization**: Generates summaries that understand speaker intent
- **Noise Robustness**: Better accuracy than Whisper in noisy environments

**Dutch Support**: Voxtral includes Dutch as one of its 8 supported languages with strong performance.

> **Note:** Function calling was originally listed as a strength but was found to be unreliable
> via vLLM deployment. This capability should be handled by the main LLM instead.

## Faster-Whisper Strengths

**Transcription Focus**: Optimized exclusively for speech-to-text:

- **Broad Language Coverage**: 50+ languages with dedicated detection
- **Mature Ecosystem**: Extensive community support and integrations
- **Unlimited Duration**: Handles any audio length via VAD-based chunking
- **Lower Complexity**: Simpler deployment for pure transcription needs
- **Efficient**: CTranslate2 backend provides excellent performance/VRAM ratio

## Decision Framework

### Choose Voxtral Mini FP8 + vLLM if you:

- Need audio understanding beyond transcription (Q&A, summarization)
- Work primarily in the 8 supported languages (especially Dutch)
- Require real-time processing with high throughput
- Value noise robustness for real-world audio quality

**Implementation**: Deploy via Docker with vLLM, expose REST API.

> **Note:** Function calling should be handled by a separate LLM (like Ministral) rather than Voxtral.

### Choose Faster-Whisper v3 Large if you:

- Need 50+ language support
- Require pure transcription without AI analysis features
- Prefer mature ecosystem with extensive community support
- Have existing Whisper-based pipelines to maintain
- Work with very long-form content requiring unlimited duration
- Want minimal VRAM footprint (~3 GB with INT8)

**Implementation**: Use faster-whisper with CTranslate2 backend.

### Hybrid Approach

For maximum flexibility, deploy both:

1. **Voxtral Mini** for Dutch content, meetings, and intelligent audio processing
2. **Faster-Whisper** for multilingual transcription and simple STT tasks

Combined VRAM: ~8 GB, leaving ample headroom on either GPU.

## Docker Deployment Examples

### Voxtral Mini via vLLM

```dockerfile
FROM vllm/vllm-openai:latest

RUN pip install mistral_common>=1.8.1

ENV MODEL_NAME="RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic"

CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "${MODEL_NAME}", \
     "--tokenizer_mode", "mistral", \
     "--config_format", "mistral", \
     "--load_format", "mistral"]
```

### Faster-Whisper

```dockerfile
FROM python:3.11-slim

RUN pip install faster-whisper

# Pre-download model
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3')"

COPY app.py /app/
CMD ["python", "/app/app.py"]
```

## Sources

1. [Mistral AI - Voxtral Model Card](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507)
2. [RedHat AI - Voxtral FP8 Quantized](https://huggingface.co/RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic)
3. [Voxtral Research Paper](https://arxiv.org/html/2507.13264v1)
4. [Faster-Whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
5. [OpenAI Whisper](https://github.com/openai/whisper)
6. [Faster-Whisper Benchmarks](https://github.com/SYSTRAN/faster-whisper/issues/1030)

---

## Conclusie & Beslissing

**Datum:** 2026-01-10

### Gekozen: Voxtral Mini 3B FP8 + vLLM

Voor het NerdCarX project kiezen we **Voxtral Mini 3B** in de **FP8 quantized** versie, geserveerd via **vLLM**.

| Aspect | Keuze |
|--------|-------|
| Model | `RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic` |
| Backend | vLLM >= 0.10.0 |
| VRAM | ~6 GB (model + overhead) |
| GPU | RTX 4090 |

### Rationale

1. **Nederlands** - Voxtral ondersteunt Nederlands als één van 8 talen
2. **Audio understanding** - Meer dan transcriptie: Q&A, summarization
3. **VRAM efficiënt** - FP8 past ruim naast Ministral LLM op RTX 4090
4. **Noise robust** - Beter dan Whisper in lawaaierige omgevingen

### Waarom niet Faster-Whisper?

- Minder robuust in lawaaierige omgeving
- 50+ talen niet nodig, we focussen op Nederlands

> **Update (2026-01-10):** Function calling was oorspronkelijk een argument voor Voxtral,
> maar bleek niet betrouwbaar te werken via vLLM. Dit is geen probleem omdat function calling
> beter past bij de LLM (Ministral) die de getranscribeerde tekst ontvangt.

### Next Steps

1. Meer info verzamelen over vLLM + Voxtral configuratie
2. Docker container bouwen met vLLM
3. Testen met Nederlandse audio samples
4. Benchmarken op RTX 4090
