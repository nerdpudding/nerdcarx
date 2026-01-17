# A2: Camera Module 3 (IMX708) Installatie

**Datum:** 2026-01-17
**Status:** ✅ COMPLEET
**Doel:** Camera Module 3 aansluiten, testen, en integreren met picamera2

---

## Wat willen we?

De OV5647 camera vervangen door Camera Module 3 (IMX708) die:

1. **Autofocus** heeft - Geen handmatige focus meer nodig
2. **Betere low-light** prestaties - HDR ondersteuning
3. **Hogere resolutie** - 12MP vs 5MP
4. **Modern software stack** - `picamera2` met `libcamera`

---

## Hardware Info

| Aspect | Specificatie |
|--------|--------------|
| Model | Raspberry Pi Camera Module 3 |
| Sensor | Sony IMX708 |
| Resolutie | 12MP (4608×2592) |
| Autofocus | Ja (PDAF) |
| HDR | Ja |
| Field of View | 66° (standaard) of 120° (wide) |
| Interface | CSI (15-pin flat cable) |
| Afmetingen | 25×24×11.5mm |

---

## Taken

### Stap 1: Hardware Installatie

> **LET OP:** Pi UITZETTEN voordat je de camera aansluit!

- [x] Pi uitzetten: `sudo shutdown now`
- [x] OV5647 camera loskoppelen (CSI kabel)
- [x] Camera Module 3 aansluiten:
  - Blauwe kant van kabel naar camera board
  - Metalen contacten naar connector op Pi
  - Klem goed dichtklikken
- [x] Pi weer aanzetten

### Stap 2: Software Verificatie

```bash
# SSH naar Pi
ssh rvanpolen@192.168.1.71

# Check of camera gedetecteerd wordt
libcamera-hello --list-cameras
```

**Verwachte output:**
```
Available cameras
-----------------
0 : imx708 [4608x2592] (/base/soc/i2c0mux/i2c@1/imx708@1a)
```

Als je geen camera ziet:
```bash
# Check of camera interface enabled is
sudo raspi-config
# → Interface Options → Camera → Enable
# Reboot nodig na wijziging
```

### Stap 3: libcamera Test (zonder Python)

```bash
# Simpele preview (5 seconden)
libcamera-hello -t 5000

# Maak een foto
libcamera-jpeg -o test_photo.jpg

# Bekijk foto info
file test_photo.jpg
```

### Stap 4: picamera2 Installeren

```bash
# Activeer conda environment
conda activate nerdcarx

# Installeer picamera2
# Let op: picamera2 heeft specifieke dependencies
pip install picamera2

# Als dat faalt, probeer:
sudo apt install -y python3-picamera2
# En dan picamera2 package linken naar conda env
```

**Alternatief via conda:**
```bash
conda install -c conda-forge libcamera
pip install picamera2
```

### Stap 5: Python Test Script

```bash
# Kopieer test script naar Pi (via rsync van desktop)
cd ~/fase3-pi/test_scripts
python test_camera_module3.py
```

Test script checkt:
- [x] Camera detectie
- [x] Foto maken
- [x] Preview window (optioneel)
- [x] Autofocus test
- [x] Low-light (night mode) test

### Stap 6: Integratie met take_photo

- [x] `pi_conversation_v3.py` aanpassen
- [x] Mock foto vervangen door echte camera capture (met fallback)
- [x] Camera shutter geluid toegevoegd
- [x] Test: "Wat zie je?" → echte foto → LLM beschrijft

**Bevindingen take_photo integratie:**
- ✅ Functie werkt end-to-end: voice command → foto → LLM beschrijving → TTS response
- ⚠️ LLM beschrijvingen zijn niet altijd accuraat
  - Onduidelijk of dit komt door:
    - Fotokwaliteit (640x480, JPEG compression)
    - Lichtcondities (binnenshuis, avond)
    - LLM model capaciteit (Ministral 14B vision)
  - Het model lijkt buiten deze app om redelijk goed te werken
  - **Later onderzoeken:** hogere resolutie, betere belichting, of ander vision model

---

## Test Commando's

```bash
# Op Pi - libcamera direct
libcamera-hello --list-cameras     # Check camera detectie
libcamera-hello -t 5000            # 5 sec preview
libcamera-jpeg -o photo.jpg        # Maak foto

# Op Pi - Python test
conda activate nerdcarx
cd ~/fase3-pi/test_scripts
python test_camera_module3.py

# Foto bekijken (via SCP naar desktop)
scp rvanpolen@192.168.1.71:~/fase3-pi/test_scripts/test_capture.jpg .
```

---

## Bekende Issues & Oplossingen

### 1. Camera niet gedetecteerd

**Symptoom:** `libcamera-hello --list-cameras` toont niets

**Oplossingen:**
1. Kabel checken (blauwe kant naar camera board)
2. Klem goed dicht?
3. Camera interface enabled? `sudo raspi-config` → Interface Options → Camera
4. Reboot na raspi-config wijziging

### 2. picamera2 import error

**Symptoom:** `ModuleNotFoundError: No module named 'picamera2'`

**Oplossing:**
```bash
# In conda env
pip install picamera2

# Of als system package (dan linken)
sudo apt install python3-picamera2
```

### 3. libcamera permission denied

**Symptoom:** `Failed to acquire camera`

**Oplossing:**
```bash
# Voeg user toe aan video groep
sudo usermod -aG video $USER
# Log opnieuw in
exit
```

### 4. Vilib werkt niet meer

**Verwacht!** Vilib (SunFounder) is voor legacy camera. Na Camera Module 3 installatie:
- `nerdcarx_web.py` werkt NIET meer (gebruikt Vilib)
- Dit is waarom we unified script nodig hebben met picamera2

---

## Verschil met OV5647

| Aspect | OV5647 | Camera Module 3 |
|--------|--------|-----------------|
| **Software** | Vilib, picamera (legacy) | picamera2, libcamera |
| **Focus** | Handmatig | Autofocus (PDAF) |
| **Low-light** | Matig | Beter (HDR) |
| **Resolutie** | 2592×1944 (5MP) | 4608×2592 (12MP) |
| **Video** | 1080p30, 720p60 | 1080p50, 720p120 |

---

## Code Snippets

### Basis foto maken

```python
from picamera2 import Picamera2
import time

# Initialiseer
camera = Picamera2()

# Configureer voor still image
config = camera.create_still_configuration()
camera.configure(config)

# Start camera
camera.start()
time.sleep(2)  # Autofocus settle time

# Maak foto
camera.capture_file("photo.jpg")
print("Foto opgeslagen: photo.jpg")

camera.stop()
```

### Foto naar base64 (voor take_photo)

```python
from picamera2 import Picamera2
import io
import base64
from PIL import Image

def capture_photo_base64(resize=(640, 480)) -> str:
    """Maak foto en return als base64 string."""
    camera = Picamera2()
    config = camera.create_still_configuration()
    camera.configure(config)
    camera.start()

    # Capture naar numpy array
    import time
    time.sleep(1)  # Autofocus

    array = camera.capture_array()
    camera.stop()

    # Converteer naar JPEG
    img = Image.fromarray(array)
    img = img.resize(resize)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')
```

### MJPEG Stream (voor web)

```python
from picamera2 import Picamera2
import io

def generate_frames():
    camera = Picamera2()
    config = camera.create_video_configuration(main={"size": (640, 480)})
    camera.configure(config)
    camera.start()

    while True:
        buffer = io.BytesIO()
        camera.capture_file(buffer, format='jpeg')
        frame = buffer.getvalue()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
```

---

## Success Criteria

- [x] `rpicam-hello --list-cameras` toont imx708 (NB: `libcamera-hello` hernoemd naar `rpicam-hello` op Trixie)
- [x] `python test_camera_module3.py` slaagt (alle 6 tests)
- [x] Foto is scherp (autofocus werkt)
- [x] Low-light foto is bruikbaar

---

## Referenties

- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [picamera2 Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [libcamera Documentation](https://libcamera.org/docs.html)

---

## Voortgang

| Datum | Update |
|-------|--------|
| 2026-01-17 | A2_TODO aangemaakt |
| 2026-01-17 | Hardware binnen, klaar voor installatie |
| 2026-01-17 | Camera Module 3 aangesloten (zonder mount, 3D print in progress) |
| 2026-01-17 | `rpicam-hello --list-cameras` → imx708 gedetecteerd |
| 2026-01-17 | libcamera Python bindings gelinkt naar conda via .pth file |
| 2026-01-17 | **ALLE 6 TESTS GESLAAGD** - Camera Module 3 volledig werkend |
| 2026-01-17 | take_photo geïntegreerd in pi_conversation_v3.py (echte camera + shutter sound) |
| 2026-01-17 | End-to-end test geslaagd: "wat zie je?" → foto → LLM beschrijft |
| 2026-01-17 | **A2 COMPLEET** - Camera Module 3 volledig geïntegreerd |

## Belangrijke Bevindingen

### 1. CLI tools hernoemd op Trixie
Op Pi OS Trixie zijn de libcamera CLI tools hernoemd:
- `libcamera-hello` → `rpicam-hello`
- `libcamera-jpeg` → `rpicam-jpeg`
- etc.

### 2. libcamera Python bindings zijn system-level
`libcamera` Python module is alleen beschikbaar via system Python (apt), niet pip.

**Oplossing voor conda:** Maak .pth file die system packages toevoegt:
```bash
echo "/usr/lib/python3/dist-packages" > \
  ~/miniforge3/envs/nerdcarx/lib/python3.13/site-packages/system-packages.pth
```

### 3. picamera2 vs Camera Module 3
- `picamera2` = Python library (versie 2)
- Camera Module 3 = hardware (IMX708 sensor)

Niet verwarren! De library werkt met alle Pi cameras.
