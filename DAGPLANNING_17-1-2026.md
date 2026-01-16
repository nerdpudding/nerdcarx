# Dagplanning 17 Januari 2026

**Focus:** Fase 3 Pi Integratie - Camera + Vision + OLED

---

## Prioriteiten

### 1. pi_conversation.py uitbreiden
**Doel:** Meer debug info zoals de desktop versie

- [ ] Timing info per stap (STT, LLM, TTS)
- [ ] Emotion display in output
- [ ] Mock foto test (function call afhandelen)
- [ ] Betere error handling
- [ ] Turn summary aan einde

**Files:** `test_scripts/pi_conversation.py`

---

### 2. Camera Module 3 installeren
**Doel:** Nieuwe camera (IMX708) werkend krijgen

- [ ] Hardware verwisselen (OV5647 → Camera Module 3)
- [ ] Boot config checken (`/boot/firmware/config.txt`)
- [ ] `rpicam-hello` testen
- [ ] Experimental scripts runnen voor basis camera test

**Files:** `experimental/` scripts

**Verwachte issues:**
- Autofocus configuratie
- Exposure/white balance tuning
- libcamera vs legacy camera stack

---

### 3. take_photo functie ECHT implementeren
**Doel:** "Wat zie je?" vraag → foto → LLM vision → beschrijving

Stappen:
- [ ] Function call `take_photo` detecteren in response
- [ ] Foto maken met camera (libcamera/picamera2)
- [ ] Foto naar desktop sturen (base64 of file upload)
- [ ] LLM vision call met foto
- [ ] Beschrijving terugsturen naar Pi

**Waar aan te passen:**
- `pi_conversation.py` - function call handling
- Orchestrator - foto ontvangen en verwerken
- Config - camera settings

**Architectuur vraag:**
- Optie A: Pi maakt foto, stuurt naar desktop via WebSocket
- Optie B: Desktop vraagt foto aan Pi, Pi stuurt terug

---

### 4. OLED emotie display (Subfase 3b)
**Doel:** show_emotion function calls afhandelen

- [ ] OLED aansluiten op I2C bus
- [ ] `luma.oled` library installeren
- [ ] Simpele emotie icons maken (of text-based eerst)
- [ ] Function call `show_emotion` detecteren
- [ ] Emotie tonen op display

**Provisorisch:** Zonder 3D-printed houder, gewoon werkend krijgen

**Hardware:** OLED WPI438 (SSD1306, 128x64, I2C @ 0x3C)

---

### 5. Experimental script uitbreiden
**Doel:** Webpagina voor handmatige control

Features:
- [ ] Rondrijden via webpagina (pijltjes of WASD)
- [ ] Wake word aan/uit toggle
- [ ] Handmatig foto maken en opslaan
- [ ] Status display (mic level, wake word status)
- [ ] Mogelijk: live camera preview

**Files:** `experimental/` folder

---

## Volgorde

| # | Taak | Geschatte inspanning |
|---|------|---------------------|
| 1 | pi_conversation.py debug info | Klein |
| 2 | Camera Module 3 installeren + test | Medium |
| 3 | take_photo implementeren | Groot |
| 4 | OLED emotie display | Medium |
| 5 | Experimental script uitbreiden | Medium-Groot |

**Realistische verwachting:** Punten 1-3 en mogelijk 4. Punt 5 als er tijd over is.

---

## Notities

- ToF sensoren en LEDs blijven op reservebank
- SLAM is Fase 4 (later)
- Hardware verwacht: Camera Module 3 (vandaag/morgen)
- Desktop orchestrator moet blijven draaien voor tests

---

## Test Commando's

```bash
# Camera test
rpicam-hello
rpicam-still -o test.jpg

# OLED test
python -c "from luma.oled.device import ssd1306; from luma.core.interface.serial import i2c; print('OK')"

# Pi conversation
conda activate nerdcarx
python ~/fase3-pi/test_scripts/pi_conversation.py
```
