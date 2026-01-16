# Fase 3: Pi Integratie - Implementatieplan

**Datum:** 2026-01-16
**Doel:** Pi client verbinden met desktop stack (STT/LLM/TTS)

---

## Overzicht

Fase 3 is opgesplitst in subfases met duidelijke prioriteiten:

| Subfase | Focus | Prioriteit | Status |
|---------|-------|------------|--------|
| **3a** | Core audio flow (wake word → VAD → WebSocket → response) | **VANDAAG** | TODO |
| **3b** | OLED emotie display | Later vandaag/morgen | TODO |
| **3c** | Hardware uitbreiding (ToF, LEDs, Camera 3) | Toekomst | Gepland |

---

## Subfase 3a: Core Audio Flow (PRIORITEIT)

### Doel

User kan via Pi mic praten met robot en krijgt response via Pi speaker:

```
[Wake word] → [VAD opname] → [WebSocket] → [Desktop: STT→LLM→TTS] → [WebSocket] → [Pi speaker]
```

### Wake Word Keuze

**Keuze: OpenWakeWord** met `hey_jarvis` model (2026-01-16)

**Stijl:** Always-listening wake-word (robot reageert op "hey jarvis" ook met TV/fans aan)

**Waarom OpenWakeWord:**
- ✅ 100% open source, geen accounts nodig
- ✅ Pre-trained modellen beschikbaar
- ✅ Laag CPU gebruik (~2-5%)
- ✅ Ingebouwde Speex noise suppression
- ✅ GitHub: https://github.com/dscripka/openWakeWord
- ✅ Reference clone: `original_openWakeWord-REFERENCE/`

**Configuratie:**
```python
from openwakeword.model import Model

model = Model(
    wakeword_models=["hey_jarvis"],
    enable_speex_noise_suppression=True  # ruisonderdrukking voor TV/fans
)

# Per audio frame (16-bit 16kHz PCM)
prediction = model.predict(audio_frame)
if prediction["hey_jarvis"] > 0.5:
    print("Wake word detected!")
```

**Later (toekomstige fase):**
- Custom "hey nerd" model trainen via [Google Colab](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb)
- Community modellen: https://github.com/fwartner/home-assistant-wakewords-collection

### VAD Keuze

**Keuze: Silero VAD via ONNX Runtime** (2026-01-16)

**Waarom Silero VAD:**
- ML-based, zeer accuraat voor speech vs noise
- Pi 5 CPU (Cortex-A76 @ 2.4GHz) is snel genoeg
- Bewezen in fase1-desktop

**BELANGRIJK: Gebruik ONNX Runtime, NIET PyTorch**
- PyTorch op ARM Pi = dependency hell
- ONNX Runtime is lichter en werkt smooth op ARM

**Fallback:** `speech_recognition` met `adjust_for_ambient_noise()` als Silero niet werkt
- Energy-threshold based (minder robuust)
- Simpeler, minder dependencies

### Audio Pipeline Samenvatting

```
[Mic plughw:2,0] → [+20dB gain in Python]
       ↓
[OpenWakeWord + Speex] → "hey jarvis" detected?
       ↓ ja
[Silero VAD (ONNX)] → spraak opnemen tot stilte
       ↓
[WebSocket] → [Desktop Orchestrator: STT→LLM→TTS]
       ↓
[Speaker plughw:3,0 + GPIO20]
```

### Implementatie Stappen

#### Stap 0: Hardware Verificatie (EERST!)

**Pi connectie:**
```bash
# SSH naar Pi
ssh rvanpolen@192.168.1.71  # of nerdcarx.local
```

**Microphone testen:**
```bash
# Check welke audio devices er zijn
arecord -l
# Output: card 2: Device [USB PnP Sound Device]

# Mic volume op 100%
alsamixer -c 2  # F4 voor Capture, pijltjes omhoog, Esc

# Test opname (5 seconden) - card 2!
arecord -D plughw:2,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav
```

**Speaker testen:**
```bash
# Check speaker devices
aplay -l
# Output: card 3: sndrpihifiberry [snd_rpi_hifiberry_dac]

# BELANGRIJK: Activeer amplifier via GPIO 20!
pinctrl set 20 op dh

# Test playback op card 3
aplay -D plughw:3,0 test.wav

# Of met speaker-test
speaker-test -D plughw:3,0 -t wav -c 1
```

**Software gain (NODIG voor huidige USB mic):**
```bash
# Optie 1: Via sox (command line)
sudo apt install sox
sox input.wav output.wav gain 20

# Optie 2: In Python (audio/capture.py) - TODO bij implementatie
# audio_data = audio_data * gain_factor
```

**Bevindingen 2026-01-16:**
- USB mic (card 2) werkt maar is zacht op >50cm afstand
- I2S speaker (card 3) werkt, vereist GPIO 20 activatie
- Software gain (~20dB via sox) is nodig voor bruikbare audio
- **TODO:** Overweeg betere far-field USB mic voor productie (bijv. ReSpeaker USB Mic Array)
- **TODO:** Mogelijk betere USB speaker, maar huidige is acceptabel

#### Stap 1: Pi Client Project Setup
```
fase3-pi/
├── pi-client/
│   ├── main.py              # Main loop
│   ├── requirements.txt     # Dependencies
│   ├── config.py            # Config (desktop IP, etc.)
│   ├── wakeword/
│   │   └── detector.py      # OpenWakeWord wrapper
│   ├── audio/
│   │   ├── vad.py           # Silero VAD (kopie van fase1)
│   │   ├── capture.py       # Mic capture
│   │   └── playback.py      # Speaker output
│   └── network/
│       └── websocket_client.py  # WebSocket naar desktop
```

#### Stap 2: Dependencies & Environment Management

**BELANGRIJK: Geen dependency hell!**

De standaard SunFounder scripts installeren alles direct op het systeem via `pip install` zonder venv. Dit willen we NIET.

**Aanpak:**
1. **Conda op Pi** (Miniforge) voor geïsoleerde environments
2. **Één environment** voor fase3 met de juiste Python versie
3. **requirements.txt** voor reproduceerbare installs
4. Later eventueel **Docker** als we meerdere services nodig hebben

**Setup Conda (eenmalig):**
```bash
# Miniforge installeren (ARM64 compatible)
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
bash Miniforge3-Linux-aarch64.sh
# Herstart shell of source ~/.bashrc

# Environment aanmaken
conda create -n nerdcarx python=3.11 -y
conda activate nerdcarx
```

**Dependencies installeren:**
```bash
conda activate nerdcarx

# System dependencies (via apt, eenmalig)
sudo apt install -y portaudio19-dev libsndfile1

# Python dependencies via pip in conda env
pip install -r requirements.txt
```

**requirements.txt:**
```
# Wake word (keuze nog open)
# openwakeword of pvporcupine

# Audio
pyaudio
numpy
soundfile

# VAD
silero-vad  # of torch + model direct

# Network
websockets
aiohttp

# Hardware (SunFounder libs - alleen wat we echt nodig hebben)
smbus2  # I2C communicatie
```

**Waarom GEEN breakout/robot-hat direct?**
De SunFounder `robot-hat` en `picar-x` libs doen veel automatische dingen (i2samp.sh, etc.) die we niet willen. We gebruiken alleen de low-level libs die we echt nodig hebben en schrijven onze eigen wrappers.

#### Stap 3: Wake Word Detector
```python
# wakeword/detector.py
from openwake_word import Model

class WakeWordDetector:
    def __init__(self, model_name="hey_jarvis"):  # of custom
        self.model = Model(wakeword_models=[model_name])

    def process(self, audio_chunk) -> bool:
        """Returns True als wake word gedetecteerd."""
        prediction = self.model.predict(audio_chunk)
        return prediction[model_name] > 0.5
```

#### Stap 4: VAD + Audio Capture
- Kopieer Silero VAD logica van fase1-desktop
- Pas aan voor Pi (eventueel andere audio device)
- Parameters: threshold=0.5, silence=1.5s, min_speech=0.3s

#### Stap 5: WebSocket Client
```python
# network/websocket_client.py
import websockets
import json
import base64

class DesktopClient:
    def __init__(self, url="ws://desktop-ip:8200/ws"):
        self.url = url
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.url)

    async def send_audio(self, audio_bytes, conversation_id="pi-session"):
        msg = {
            "type": "audio_process",
            "conversation_id": conversation_id,
            "timestamp": time.time(),
            "payload": {
                "audio_base64": base64.b64encode(audio_bytes).decode(),
                "language": "nl"
            }
        }
        await self.ws.send(json.dumps(msg))

    async def receive_response(self):
        """Ontvang response + audio chunks."""
        while True:
            msg = json.loads(await self.ws.recv())
            if msg["type"] == "audio_chunk":
                yield msg["payload"]
            elif msg["type"] == "response":
                # Laatste message
                break
```

#### Stap 6: Main Loop
```python
# main.py
async def main():
    wake_detector = WakeWordDetector()
    vad = SileroVAD()
    client = DesktopClient("ws://192.168.x.x:8200/ws")
    await client.connect()

    while True:
        # 1. Luister naar wake word
        audio = capture_audio_stream()
        if wake_detector.process(audio):
            print("Wake word gedetecteerd!")

            # 2. Start VAD opname
            recorded_audio = vad.record_until_silence()

            # 3. Stuur naar desktop
            await client.send_audio(recorded_audio)

            # 4. Ontvang en speel audio af
            async for chunk in client.receive_response():
                play_audio(chunk["audio_base64"])
```

#### Stap 7: Testen
```bash
# Op Pi
cd fase3-pi/pi-client
source ~/nerdcarx-env/bin/activate
python main.py

# Test: zeg "hey jarvis" (of gekozen wake word) + vraag
```

### Success Criteria Subfase 3a

- [ ] Wake word detectie werkt op Pi
- [ ] VAD neemt spraak correct op
- [ ] Audio wordt naar desktop gestuurd via WebSocket
- [ ] Desktop verwerkt (STT → LLM → TTS)
- [ ] TTS audio komt terug naar Pi
- [ ] Audio speelt af via Pi speaker
- [ ] End-to-end latency < 5s (acceptabel)

---

## Subfase 3b: OLED Emotie Display (LATER)

### Hardware
- OLED WPI438 (SSD1306, 128x64, I2C @ 0x3C)
- Aanwezig, nog niet aangesloten

### Implementatie
1. OLED aansluiten op I2C bus
2. `luma.oled` library installeren
3. Emotie PNG assets maken (of tekst-based)
4. `show_emotion` handler toevoegen aan Pi client
5. Function calls van desktop afhandelen

### Voorbeeld
```python
# handlers/oled.py
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c

class OLEDDisplay:
    def __init__(self):
        serial = i2c(port=1, address=0x3C)
        self.device = ssd1306(serial)

    def show_emotion(self, emotion: str):
        # Toon emotie op display
        ...
```

---

## Subfase 3c: Hardware Uitbreiding (TOEKOMST)

**Niet nu implementeren.** Komt later wanneer hardware binnen is:

- ToF sensoren (VL53L0X) via I2C hub - **Besteld**
- Grove LEDs op D0/D1 - **Besteld**
- Camera Module 3 (IMX708) - **Besteld**
- YOLO safety layer
- SLAM navigatie

---

## Desktop Aanpassingen Nodig

De fase2 orchestrator is al voorbereid met WebSocket, maar check:

1. ✅ WebSocket endpoint `/ws` - werkt (getest)
2. ✅ `audio_process` message handling - geïmplementeerd
3. ⚠️ TTS audio terug via WebSocket - verifieer dat `audio_chunk` messages correct verstuurd worden
4. ⚠️ Function calls doorsturen naar Pi - verifieer `function_call` message flow

---

## Verificatie Commands

```bash
# 1. Check Pi netwerk
ping 192.168.1.71  # of nerdcarx.local

# 2. Check desktop stack draait
curl http://localhost:8200/health

# 3. Test WebSocket vanaf Pi
python3 -c "import websockets; print('OK')"

# 4. Run pi-client
cd fase3-pi/pi-client
python main.py
```

---

## Risico's en Mitigaties

| Risico | Mitigatie |
|--------|-----------|
| OpenWakeWord werkt niet goed | Fallback naar Porcupine (eenmalig account) |
| Audio device issues op Pi | Test eerst met `arecord`/`aplay` |
| WebSocket connectie onstabiel | Auto-reconnect logica toevoegen |
| Latency te hoog | Profile waar bottleneck zit |

---

## Open Vragen

1. **Wake word keuze**: OpenWakeWord of Porcupine? User doet research.
2. ~~**Desktop IP**~~: ✅ 192.168.1.71 of nerdcarx.local
3. **Audio format**: WAV 16kHz mono (zelfde als fase1) - te verifiëren na mic test

---

## Volgende Stap

Na goedkeuring van dit plan:
1. **SSH naar Pi** en test verbinding
2. **Test microphone** met `arecord`
3. **Test speaker** met `aplay`
4. Als hardware werkt → wake word keuze maken
5. Dan pas project setup en implementatie

---

## Hardware Checklist

### Compute & Controller
- [x] Raspberry Pi 5 (16GB RAM)
- [x] RobotHAT v4 (geïnstalleerd)
- [x] Active cooler voor Pi 5
- [x] SD card (128GB)
- [x] Netwerk: Pi en Desktop op zelfde LAN

### PiCar-X Kit (geïnstalleerd)
- [x] DC motors (2x)
- [x] Servo's (steering P2, pan P0, tilt P1)
- [x] Ultrasonic HC-SR04 (D2/D3)
- [x] Grayscale module (A0-A2)

### Camera
- [x] Camera OV5647 - werkend, wordt vervangen
- [ ] **Camera Module 3 (IMX708)** - Besteld

### I2C Devices
- [ ] **OLED WPI438 (SSD1306)** - Aanwezig, nog niet aangesloten
- [ ] **TCA9548A I2C Hub** - Besteld
- [ ] **2x VL53L0X ToF sensoren** - Besteld
- [ ] Grove kabels - Besteld

### Indicators
- [ ] **2x Grove LED (wit)** - Besteld (voor D0/D1)
- [ ] Grove→Dupont adapters - Besteld

### Audio
- [x] I2S speaker (mono) - werkend
- [x] USB microfoon - aanwezig, nog niet getest met AI

> **Hardware reference:** [docs/hardware/HARDWARE-REFERENCE.md](../docs/hardware/HARDWARE-REFERENCE.md)

---

## Voortgang

| Datum | Update |
|-------|--------|
| 2026-01-14 | Hardware geassembleerd en basis tests succesvol |
| 2026-01-14 | Pi OS Lite (Trixie 64-bit) geïnstalleerd |
| 2026-01-14 | SunFounder libraries geïnstalleerd (robot-hat, vilib, picar-x) |
| 2026-01-14 | Motoren, servo's en I2S speaker getest - werkend |
| 2026-01-14 | Camera werkend maar exposure tuning nodig (donker beeld) |
| 2026-01-16 | Fase 3 plan gedetailleerd met subfases 3a/3b/3c |
| 2026-01-16 | Audio hardware getest: mic=card2, speaker=card3, GPIO20 nodig, +20dB gain via sox |
| 2026-01-16 | Wake word: OpenWakeWord (hey_jarvis), VAD: Silero via ONNX (niet PyTorch) |

---

[← Fase 2](../fase2-refactor/PLAN.md) | [Terug naar README](../README.md)
