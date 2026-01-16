# Dagplanning 17 Januari 2026

**Focus:** Fase 3 Pi Integratie - Camera + Vision + OLED

---

## Aanpak: Mock eerst, dan Echt

De implementatie volgt twee stappen:

1. **Mock tests** - Valideer de function call flow met dummy data
2. **Echte implementatie** - Na hardware installatie, volledig werkend maken

---

## Fase A: Mock Tests (zonder nieuwe hardware)

### A1. pi_conversation.py uitbreiden
**Doel:** Debug info + mock function call handling

- [ ] Timing info per stap (STT, LLM, TTS)
- [ ] Emotion display in console output
- [ ] **Mock foto test**: detecteer `take_photo` call, return "Mock: geen camera" of placeholder
- [ ] **Mock emotie test**: detecteer `show_emotion` call, print naar console
- [ ] Betere error handling
- [ ] Turn summary aan einde

**Files:** `test_scripts/pi_conversation.py`

**Resultaat:** Function call infrastructure gevalideerd zonder nieuwe hardware.

---

## Fase B: Hardware Installatie (als pakket binnen is)

### B1. Camera Module 3 installeren
**Doel:** Nieuwe camera (IMX708) werkend krijgen

- [ ] Hardware verwisselen (OV5647 → Camera Module 3)
- [ ] Boot config checken (`/boot/firmware/config.txt`)
- [ ] `rpicam-hello` testen
- [ ] Experimental scripts runnen voor basis camera test

**Verwachte issues:**
- Autofocus configuratie
- Exposure/white balance tuning
- libcamera vs legacy camera stack

### B2. OLED aansluiten
**Doel:** Display hardware werkend

- [ ] OLED aansluiten op I2C bus
- [ ] `i2cdetect` check (0x3C)
- [ ] `luma.oled` library installeren
- [ ] Simpele test: text op scherm

**Hardware:** OLED WPI438 (SSD1306, 128x64, I2C @ 0x3C)

---

## Fase C: Echte Implementatie (na hardware setup)

### C1. take_photo functie ECHT implementeren
**Doel:** "Wat zie je?" vraag → foto → LLM vision → beschrijving

- [ ] Function call `take_photo` detecteren in response
- [ ] Foto maken met camera (libcamera/picamera2)
- [ ] Foto naar desktop sturen (base64 via WebSocket)
- [ ] LLM vision call met foto
- [ ] Beschrijving terugsturen naar Pi

**Waar aan te passen:**
- `pi_conversation.py` - function call handling
- Orchestrator - foto ontvangen en verwerken

### C2. OLED emotie display ECHT implementeren
**Doel:** show_emotion function calls → display

- [ ] Simpele emotie icons maken (of text-based eerst)
- [ ] Function call `show_emotion` detecteren
- [ ] Emotie tonen op display

**Provisorisch:** Zonder 3D-printed houder, gewoon werkend krijgen

---

## Optioneel: Experimental script uitbreiden
**Doel:** Webpagina voor handmatige control (als er tijd over is)

- [ ] Rondrijden via webpagina (pijltjes of WASD)
- [ ] Wake word aan/uit toggle
- [ ] Handmatig foto maken en opslaan
- [ ] Status display (mic level, wake word status)

**Files:** `experimental/` folder

---

## Volgorde Samenvatting

| Fase | Taak | Afhankelijkheid |
|------|------|-----------------|
| A1 | Mock tests in pi_conversation.py | Geen (nu te doen) |
| B1 | Camera Module 3 installeren | Hardware binnen |
| B2 | OLED aansluiten | Hardware binnen |
| C1 | take_photo ECHT | B1 afgerond |
| C2 | OLED emotie ECHT | B2 afgerond |

**Realistische verwachting:** Fase A vandaag, Fase B zodra hardware binnen is, Fase C daarna.

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
