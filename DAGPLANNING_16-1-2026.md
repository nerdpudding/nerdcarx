# Dagplanning 16 januari 2026

**Status:** Planning voor vandaag

---

## Overzicht

| # | Taak | Prioriteit | Geschatte tijd |
|---|------|------------|----------------|
| 1 | TODO Fase 1 afmaken | Hoog | - |
| 2 | VAD op Pi + pipeline test script | Hoog | - |
| 3 | OLED aansluiten + emotion features | Medium (indien tijd) | - |

---

## 1. TODO Fase 1 Afmaken

Laatste config items voor de VAD/STT/LLM/TTS pipeline.

Zie: [`fase1-desktop/TODO.md`](../../fase1-desktop/TODO.md)

**Belangrijkste punten:**
- Text normalisatie voor TTS (Engelse afkortingen → Nederlandse uitspraak)
- System prompt aanpassing (Nederlandse voorkeur)
- Temperature/top_p tuning (optioneel)

---

## 2. VAD op Pi + Pipeline Test Script

**Huidige situatie Pi:**
- PiCar-X gebouwd en basis getest
- Standaard hardware config
- Nog GEEN: OLED scherm, Camera Module 3, ToF sensors, extra LEDs
- WEL aanwezig: mic (USB), speaker (I2S)

**Doel:**
1. VAD werkend krijgen op de Pi
2. Script maken om LLM pipeline te testen
3. Test: praten via car mic → desktop processing → antwoord via car speaker

**Wat nodig is:**
- VAD setup op Pi (Silero of vergelijkbaar)
- Network verbinding Pi ↔ Desktop orchestrator
- Audio capture (mic) en playback (speaker) op Pi
- Test script voor end-to-end flow

---

## 3. OLED Aansluiten + Emotion Features (indien tijd)

**Huidige situatie:**
- OLED WPI438 (SSD1306) aanwezig
- Nog niet aangesloten

**Doel:**
- OLED aansluiten op I2C bus
- Test met luma.oled
- Emotion display integreren met orchestrator responses

---

## Later (niet vandaag)

- **Fase 2**: Refactoring, dockerizen
- **Wachten op hardware**: Camera Module 3, ToF sensors, LEDs
- **Hardware aansluiten**: Onder fase 2/3
- **Documenteren**: Alles netjes bijwerken
- **Fase 4**: Autonomie features

---

## Hardware Status Reminder

**Aanwezig en werkend:**
- Pi 5 (16GB) met Pi OS Lite
- RobotHAT v4
- Motoren en servo's
- I2S speaker (mono)
- USB microfoon
- Camera OV5647 (wordt vervangen)

**Aanwezig, nog niet aangesloten:**
- OLED WPI438 (SSD1306)

**Besteld/te bestellen:**
- Camera Module 3 (IMX708)
- TCA9548A I2C Hub
- 2x VL53L0X ToF sensoren
- 2x Grove LED (wit)
- Grove kabels

---

## Notities

*Voeg hier notities toe tijdens het werken*
