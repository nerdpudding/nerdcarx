# Fase 3: Pi Integratie - Implementatieplan

**Datum:** 2026-01-16
**Doel:** Pi client verbinden met desktop stack (STT/LLM/TTS)

---

## Overzicht

Fase 3 is opgesplitst in subfases met duidelijke prioriteiten:

| Subfase | Focus | Prioriteit | Status |
|---------|-------|------------|--------|
| **3a** | Core audio flow (wake word → VAD → WebSocket → response) | - | ✅ DONE (2026-01-17) |
| **3a+** | Modulaire Pi client + Remote function calls (take_photo) | **NU** | TODO |
| **3b** | OLED emotie display | Na 3a+ | TODO |
| **3c** | Hardware uitbreiding (ToF, LEDs, Camera 3) | Na hardware | 🔄 Camera 3 eerst |

---

## Subfase 3a: Core Audio Flow (PRIORITEIT)

### Doel

User kan via Pi mic praten met robot en krijgt response via Pi speaker:

```
[Wake word] → [VAD opname] → [WebSocket] → [Desktop: STT→LLM→TTS] → [WebSocket] → [Pi speaker]
```

### Wake Word Keuze

**Keuze: OpenWakeWord v0.4.0** met `hey_jarvis` model (2026-01-16) ✅ WERKEND

**Stijl:** Always-listening wake-word (robot reageert op "hey jarvis" ook met TV/fans aan)

**Waarom OpenWakeWord:**
- ✅ 100% open source, geen accounts nodig
- ✅ Pre-trained modellen beschikbaar
- ✅ Laag CPU gebruik (~2-5%)
- ✅ Ingebouwde Speex noise suppression
- ✅ GitHub: https://github.com/dscripka/openWakeWord
- ✅ Reference clone: `original_openWakeWord-REFERENCE/`

**KRITIEK: Gebruik versie 0.4.0, NIET 0.6.0!**
- v0.6.0 faalt: `tflite-runtime` heeft geen wheel voor Python 3.13 ARM64
- v0.4.0 werkt: gebruikt ONNX Runtime

**Test resultaten:** Scores 0.85-1.00 bij duidelijke "hey jarvis"

**Configuratie (v0.4.0 API - geen kwargs!):**
```python
from openwakeword.model import Model

# v0.4.0: Model() zonder parameters laadt alle pre-trained models
model = Model()

# Per audio frame (16-bit 16kHz PCM, 1280 samples = 80ms)
prediction = model.predict(audio_frame)
if prediction["hey_jarvis"] > 0.5:
    print("Wake word detected!")
```

**Test script:** `test_scripts/test_wakeword.py`

**Later (toekomstige fase):**
- Custom "hey nerd" model trainen via [Google Colab](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb)
- Community modellen: https://github.com/fwartner/home-assistant-wakewords-collection

### VAD Keuze

**Keuze: Silero VAD v4 via ONNX Runtime** (2026-01-16) ✅ WERKEND

**Waarom Silero VAD:**
- ML-based, zeer accuraat voor speech vs noise
- Pi 5 CPU (Cortex-A76 @ 2.4GHz) is snel genoeg
- Bewezen in fase1-desktop

**BELANGRIJK: Gebruik ONNX Runtime, NIET PyTorch**
- PyTorch op ARM Pi = dependency hell
- ONNX Runtime is lichter en werkt smooth op ARM

**KRITIEK: Gebruik Silero VAD v4 model, NIET nieuwere versies!**
- v4 model: inputs `h`/`c` (shape 2,1,64) - WERKT
- Nieuwere versies: input `state` (shape 128) - WERKT NIET correct
- Download URL: `https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.onnx`
- Chunk size: 480 samples (30ms @ 16kHz)

**Test script:** `test_scripts/test_vad.py`

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

- [x] Wake word detectie werkt op Pi ✅ (2026-01-16)
- [x] VAD neemt spraak correct op ✅ (2026-01-16)
- [x] Audio wordt naar desktop gestuurd via WebSocket ✅ (2026-01-17)
- [x] Desktop verwerkt (STT → LLM → TTS) ✅ (2026-01-17)
- [x] TTS audio komt terug naar Pi ✅ (2026-01-17)
- [x] Audio speelt af via Pi speaker ✅ (2026-01-17)
- [x] End-to-end latency < 5s (acceptabel) ✅ (2026-01-17)

**Subfase 3a: ✅ COMPLEET** (2026-01-17)

---

## Subfase 3a+: Modulaire Pi Client + Remote Function Calls

**Status:** TODO
**Doel:** Modulaire code structuur + foto's maken op Pi en meesturen naar orchestrator

### Probleem

Huidige situatie:
- `pi_conversation_v2.py` is één groot script (~800 regels)
- Orchestrator voert `take_photo` lokaal uit met mock image op desktop
- Pi krijgt `function_call` messages alleen als notificatie, niet voor execution

Gewenste situatie:
- Modulaire Pi client code (herbruikbaar, uitbreidbaar)
- LLM roept `take_photo` aan → Pi maakt foto → stuurt naar orchestrator → LLM analyseert
- Voorbereid op toekomstige tools: `show_emotion` (OLED), `drive`, `set_leds`

### WebSocket Protocol Uitbreiding

Nieuwe message types voor round-trip function execution:

```
Desktop → Pi:
  FUNCTION_REQUEST: {
    "type": "function_request",
    "payload": {
      "name": "take_photo",
      "arguments": {"question": "wat zie je?"},
      "request_id": "uuid"
    }
  }

Pi → Desktop:
  FUNCTION_RESULT: {
    "type": "function_result",
    "payload": {
      "request_id": "uuid",
      "name": "take_photo",
      "result": "foto gemaakt",
      "image_base64": "..."  # optioneel, voor vision
    }
  }
```

### Tool Categorisatie

| Tool | Locatie | Reden |
|------|---------|-------|
| `take_photo` | Pi (remote) | Camera zit op Pi |
| `show_emotion` | Pi (remote) | OLED zit op Pi |
| Toekomst: `drive`, `set_leds` | Pi (remote) | Hardware op Pi |

### Pi Client Package Structuur

```
fase3-pi/
├── pi_client/                    # Python package
│   ├── __init__.py
│   ├── config.py                 # Configuratie (IP, device names)
│   │
│   ├── core/                     # Core componenten
│   │   ├── __init__.py
│   │   ├── client.py             # NerdCarXClient main class
│   │   └── websocket.py          # WebSocket + FUNCTION_REQUEST handling
│   │
│   ├── audio/                    # Audio componenten
│   │   ├── __init__.py
│   │   ├── capture.py            # Mic capture + resampling
│   │   ├── playback.py           # Speaker playback
│   │   ├── vad.py                # Silero VAD wrapper
│   │   └── wakeword.py           # OpenWakeWord wrapper
│   │
│   ├── tools/                    # Function call handlers
│   │   ├── __init__.py
│   │   ├── base.py               # PiTool protocol
│   │   ├── registry.py           # PiToolRegistry
│   │   ├── camera.py             # take_photo (mock → real)
│   │   └── display.py            # show_emotion (console → OLED)
│   │
│   └── hardware/                 # Hardware abstracties (stub voor nu)
│       ├── __init__.py
│       ├── camera.py             # Camera capture (mock eerst)
│       └── oled.py               # OLED control (stub)
│
├── run_conversation.py           # Entry point
├── test_scripts/                 # Bestaande scripts (behouden)
└── requirements.txt
```

### Orchestrator Aanpassingen

**1. Protocol uitbreiden** (`websocket/protocol.py`):
- `FUNCTION_REQUEST` message type
- `FUNCTION_RESULT` message type
- `FunctionRequestMessage` en `FunctionResultMessage` dataclasses

**2. Tool marking** (`services/tools/base.py`):
```python
@property
def is_remote(self) -> bool:
    """True als tool op Pi moet worden uitgevoerd."""
    return False  # Default: lokaal
```

**3. Vision tool remote maken** (`services/tools/vision.py`):
```python
@property
def is_remote(self) -> bool:
    return True  # Camera zit op Pi
```

**4. Handler aanpassen** (`websocket/handlers.py`):
- In `_process_tool_calls()`: check `tool.is_remote`
- Als remote: stuur `FUNCTION_REQUEST`, wacht op `FUNCTION_RESULT`
- Gebruik result (incl. image_base64) in LLM chain

### Pi Client Design Patterns

**1. Protocol Pattern (spiegelt orchestrator)**:
```python
# pi_client/tools/base.py
@runtime_checkable
class PiTool(Protocol):
    @property
    def name(self) -> str: ...

    async def execute(self, arguments: dict) -> dict:
        """Returns dict met result + optioneel image_base64."""
        ...
```

**2. Registry Pattern**:
```python
# pi_client/tools/registry.py
class PiToolRegistry:
    def register(self, tool: PiTool) -> None: ...
    async def execute(self, name: str, args: dict) -> dict: ...
```

### Implementatie Stappen

1. **Protocol uitbreiden** (orchestrator)
2. **Tool is_remote property** (orchestrator)
3. **Handler remote logic** (orchestrator)
4. **Pi client package maken** (extractie uit v2)
5. **Camera tool** (mock eerst, later picamera2)
6. **Display tool** (console eerst, later luma.oled)
7. **Entry point** (`run_conversation.py`)

### Success Criteria

- [ ] "Wat zie je?" → Pi stuurt mock foto → LLM beschrijft
- [ ] Multi-turn conversatie zonder opnieuw wake word
- [ ] Emotie changes zichtbaar in console
- [ ] `test_scripts/pi_conversation_v2.py` blijft werken (backward compatible)

### Toekomst Extensibility

| Feature | Module |
|---------|--------|
| Echte camera | `hardware/camera.py` |
| OLED display | `hardware/oled.py` |
| Motor control | `hardware/motion.py` + `tools/motion.py` |
| Object detection | `perception/yolo.py` |
| SLAM | `navigation/slam.py` |

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

1. ~~**Wake word keuze**~~: ✅ OpenWakeWord v0.4.0 met `hey_jarvis` model (getest, werkt)
2. ~~**Desktop IP**~~: ✅ 192.168.1.71 of nerdcarx.local
3. ~~**Audio format**~~: ✅ WAV 16kHz mono, +20dB gain nodig voor USB mic

---

## Volgende Stap

### ✅ Subfase 3a COMPLEET (2026-01-17)
- ✅ Hardware: mic (card 2), speaker (card 3 + GPIO 20)
- ✅ Wake word: OpenWakeWord v0.4.0 met hey_jarvis
- ✅ VAD: Silero VAD v4 via ONNX Runtime
- ✅ WebSocket: audio_process → response + audio_chunks
- ✅ pi_conversation.py: volledige flow werkend (6 turns getest)

### Volgende prioriteiten (Jan 17+)
1. **pi_conversation.py uitbreiden** - Meer debug info (timing, emotion display, zoals desktop versie)
2. **Camera Module 3** installeren en testen (hardware binnen)
3. **take_photo functie ECHT implementeren** - Foto maken → LLM vision → beschrijving
4. **OLED emotie display** (Subfase 3b) - show_emotion function calls afhandelen
5. **Experimental script uitbreiden** - Webpagina control, wakeword toggle, handmatige foto

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
| 2026-01-16 | Conda (Miniforge) + Python 3.13 environment opgezet |
| 2026-01-16 | **OpenWakeWord v0.4.0** werkend - `test_scripts/test_wakeword.py` (scores 0.85-1.00) |
| 2026-01-16 | **Silero VAD v4 ONNX** werkend - `test_scripts/test_vad.py` (h/c state, 480 chunk) |
| 2026-01-16 | SETUP.md aangemaakt met complete installatie instructies en troubleshooting |
| 2026-01-17 | **pi_conversation.py** werkend - volledige flow: wake → VAD → WebSocket → TTS playback |
| 2026-01-17 | End-to-end test succesvol: 6 turns, function calls (emotion, take_photo) ontvangen |

---

[← Fase 2](../fase2-refactor/Fase2_Implementation_Plan.md) | [Terug naar README](../README.md)
