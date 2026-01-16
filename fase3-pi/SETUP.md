# Fase 3 Pi Setup Guide

Stap-voor-stap installatie instructies voor de Pi client.

**Getest op:** Raspberry Pi 5 (16GB), Pi OS Lite (Trixie 64-bit), Python 3.13.5

---

## 1. Audio Hardware Configuratie

### 1.1 Check audio devices

```bash
# Microfoon
arecord -l
# Output: card 2: Device [USB PnP Sound Device]

# Speaker
aplay -l
# Output: card 3: sndrpihifiberry [snd_rpi_hifiberry_dac]
```

### 1.2 Microfoon testen

```bash
# Volume op 100%
alsamixer -c 2
# Druk F4 (Capture), pijltjes omhoog tot 100%, Esc

# Test opname (5 sec)
arecord -D plughw:2,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav
```

### 1.3 Speaker testen

```bash
# BELANGRIJK: Activeer amplifier via GPIO 20
pinctrl set 20 op dh

# Test playback
aplay -D plughw:3,0 test.wav

# Of speaker-test
speaker-test -D plughw:3,0 -t wav -c 1
```

### 1.4 Software gain (nodig voor USB mic op afstand)

De USB mic is zacht op >50cm afstand. Gebruik +20dB gain:

```bash
# Via sox
sudo apt install sox
sox input.wav output.wav gain 20

# Of in Python (zie audio/capture.py)
```

---

## 2. Conda Environment Setup

### 2.1 Miniforge installeren

```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
bash Miniforge3-Linux-aarch64.sh
```

Bij vraag "initialize conda?" → typ `yes`

```bash
# Herstart shell
source ~/.bashrc

# Verify
conda --version
```

### 2.2 Environment aanmaken

```bash
conda create -n nerdcarx python=3.13 -y
conda activate nerdcarx
```

### 2.3 ISSUE: Oude packages in ~/.local

Als je eerder pip install deed buiten conda, kunnen oude packages conflicten veroorzaken.

**Oplossing:**
```bash
rm -rf ~/.local/lib/python3.13/site-packages
```

---

## 3. OpenWakeWord Installatie

### 3.1 Installeer openwakeword

```bash
conda activate nerdcarx
pip install openwakeword==0.4.0
```

**ISSUE:** Versie 0.6.0 faalt met `tflite-runtime` (geen wheel voor Python 3.13 ARM64)

**Oplossing:** Gebruik versie 0.4.0 - werkt met ONNX Runtime

### 3.2 Test installatie

```bash
python -c "import openwakeword; print('OK')"
```

**Verwachte warnings (negeren):**
- `GPU device discovery failed` - normaal, Pi heeft geen GPU
- `CUDAExecutionProvider not available` - normaal, gebruikt CPU

### 3.3 Test models laden

```bash
python -c "from openwakeword.model import Model; m = Model(); print('Models:', list(m.models.keys()))"
```

**Verwachte output:**
```
Models: ['alexa', 'hey_mycroft', 'hey_jarvis', 'timer', 'weather']
```

---

## 4. PyAudio Installatie

```bash
pip install pyaudio
```

**ALSA warnings bij gebruik (negeren):**
- `Unknown PCM surround*` - pyaudio probeert alle configs
- `jack server is not running` - we gebruiken geen jack
- `Cannot open device /dev/dsp` - oude OSS, niet nodig

---

## 5. Wake Word Test

### 5.1 Test script

Maak `test_wakeword.py`:

```python
import pyaudio
import numpy as np
from openwakeword.model import Model

# v0.4.0 API - load all models, no kwargs
model = Model()

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280, input_device_index=2)

print(f"Loaded models: {list(model.models.keys())}")
print("Listening for 'hey jarvis'... (Ctrl+C to stop)")

while True:
    data = np.frombuffer(stream.read(1280), dtype=np.int16)
    prediction = model.predict(data)
    score = prediction["hey_jarvis"]
    if score > 0.5:
        print(f"DETECTED! Score: {score:.2f}")
```

### 5.2 Run test

```bash
conda activate nerdcarx
python test_wakeword.py
```

Zeg "hey jarvis" - je zou `DETECTED! Score: 0.9x` moeten zien.

---

## 6. Bekende Issues & Oplossingen

| Issue | Oorzaak | Oplossing |
|-------|---------|-----------|
| `tflite-runtime` not found | Geen wheel voor Py3.13 ARM64 | Gebruik openwakeword 0.4.0 |
| Mic te zacht op afstand | USB mic beperking | +20dB gain via sox of Python |
| Speaker geen geluid | Amplifier niet actief | `pinctrl set 20 op dh` |
| GPU warnings | Geen GPU op Pi | Negeren, gebruikt CPU |
| ALSA warnings | PyAudio probeert alle configs | Negeren |
| Old packages conflict | ~/.local/lib packages | Verwijder ~/.local/lib/python3.13 |

---

## 7. Hardware Referentie

| Component | Device | Card |
|-----------|--------|------|
| USB Microfoon | plughw:2,0 | card 2 |
| I2S Speaker | plughw:3,0 | card 3 |
| Speaker Enable | GPIO 20 | `pinctrl set 20 op dh` |

---

## Volgende Stappen

- [ ] Silero VAD via ONNX Runtime testen
- [ ] Gain in Python implementeren
- [ ] WebSocket client naar desktop
- [ ] Volledige pipeline integreren
