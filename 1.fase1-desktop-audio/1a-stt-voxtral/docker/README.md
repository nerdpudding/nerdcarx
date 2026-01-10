# Voxtral Mini - Docker Setup

> **Doel:** Voxtral Mini 3B draaien via vLLM in Docker, testen met audio samples.

---

## Vereisten

- Ubuntu met Docker geïnstalleerd
- NVIDIA GPU (RTX 4090 aanbevolen)
- NVIDIA Container Toolkit geïnstalleerd
- ~15 GB vrije schijfruimte (model download)
- **~10-12 GB VRAM beschikbaar**

> **Let op:** We gebruiken het originele model (bf16, ~9.5GB VRAM).
> De FP8 quantized versie werkt niet met vLLM. Zie `../models/README.md` voor details.

---

## Stap-voor-stap

### Stap 1: Controleer NVIDIA Docker support

```bash
# Check of nvidia-container-toolkit geïnstalleerd is
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
```

Als dit niet werkt, installeer eerst nvidia-container-toolkit:
```bash
# Voeg NVIDIA repo toe (als nog niet gedaan)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Stap 2: Bouw en start de Voxtral container

Vanuit deze map (`1a-stt-voxtral/docker/`):

```bash
# Eerste keer: bouw custom image met audio dependencies
docker compose build

# Start de container
docker compose up -d
```

**Eerste keer duurt lang:**
1. Docker image build (~2-5 min)
2. Model download (~12 GB) naar `~/.cache/huggingface/`

Monitor de voortgang:
```bash
docker compose logs -f
```

Wacht tot je ziet:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Stap 3: Test of de server draait

```bash
curl http://localhost:8150/health
```

Verwachte output: `{"status":"healthy"}`

Check welke modellen geladen zijn:
```bash
curl http://localhost:8150/v1/models | jq
```

### Stap 4: Test transcriptie met een audio sample

Download een test audio file:
```bash
# Maak test map aan
mkdir -p ../test-audio
cd ../test-audio

# Download Obama sample (gebruikt in HuggingFace voorbeelden)
pip install huggingface_hub
python3 -c "from huggingface_hub import hf_hub_download; print(hf_hub_download('patrickvonplaten/audio_samples', 'obama.mp3', repo_type='dataset'))"
```

Of gebruik een eigen audio bestand (MP3, WAV, etc.).

### Stap 5: Test transcriptie via Python

Installeer dependencies (eenmalig):
```bash
pip install openai mistral_common[audio]
```

Run het test script:
```bash
cd ../docker
python3 test_transcription.py ../test-audio/obama.mp3
```

Of interactief:
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8150/v1", api_key="dummy")

# Open audio file
with open("pad/naar/audio.mp3", "rb") as f:
    response = client.audio.transcriptions.create(
        model="mistralai/Voxtral-Mini-3B-2507",
        file=f,
        language="nl"  # of "en" voor Engels
    )

print(response.text)
```

### Stap 6: Test audio understanding (Q&A)

```bash
python3 test_audio_qa.py ../test-audio/obama.mp3 "What is this person talking about?"
```

---

## Stoppen

```bash
docker compose down
```

---

## Troubleshooting

### "CUDA out of memory"

Verlaag de context length in `docker-compose.yml`:
```yaml
command: >
  ... --max-model-len 2048
```

Of verlaag GPU memory utilization:
```yaml
command: >
  ... --gpu-memory-utilization 0.80
```

### Model download mislukt

Check of je genoeg schijfruimte hebt:
```bash
df -h ~/.cache
```

### Container start niet

Check logs:
```bash
docker compose logs
```

---

## VRAM Gebruik

| Component | VRAM |
|-----------|------|
| Voxtral Mini (bf16) | ~9.5 GB |
| KV Cache (4096 context) | ~1-2 GB |
| **Totaal** | **~10-12 GB** |

> **Note:** GPU0 (RTX 4090, 24GB) heeft nog ~12-14GB over voor de LLM.
> Later onderzoeken of Voxtral naar GPU1 (5070 Ti) kan.

---

## Volgende stappen

Na succesvolle test:
1. [ ] Test met Nederlandse audio samples
2. [ ] Meet VRAM gebruik (`nvidia-smi`)
3. [ ] Meet latency voor typische utterances
4. [ ] Integreer met microphone input (fase 1a volgende stap)

---

[← Terug naar 1a Plan](../PLAN.md)
