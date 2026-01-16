# Dagplanning 16 januari 2026

**Status:** ✅ Fase 1 AFGEROND | 🔄 Fase 2 IN PROGRESS

---

## Overzicht

| # | Taak | Prioriteit | Status |
|---|------|------------|--------|
| 1 | TODO Fase 1 afmaken | Hoog | ✅ AFGEROND |
| 2 | Fase 2 Docker Stack opzetten | Hoog | ✅ AFGEROND |
| 3 | WebSocket testen (zonder Pi) | Medium | ⏳ TODO |
| 4 | VAD op Pi + pipeline test script | Medium | Gepland voor Fase 3 |
| 5 | OLED aansluiten + emotion features | Medium | Gepland voor Fase 3 |

---

## 1. TODO Fase 1 Afmaken - ✅ AFGEROND

**Wat is geïmplementeerd:**
- ✅ Text normalisatie: acroniemen → NL fonetiek ("API" → "aa-pee-ie")
- ✅ Getallen → woorden ("247" → "tweehonderdzevenenveertig")
- ✅ 30s ElevenLabs reference audio met alle emoties
- ✅ Pseudo-streaming: TTS per zin via SSE (~3x snellere perceived latency)
- ✅ Spatiebalk interrupt tijdens audio playback
- ✅ Gedetailleerde timing output per turn
- ✅ Terminal restore na exit

**Bekende beperkingen (acceptabel):**
- Sommige woorden klinken Engels (Fish Audio limitatie)
- Vraagintonatie niet altijd correct (model limitatie)

Zie: [`fase1-desktop/TODO.md`](fase1-desktop/TODO.md) voor volledige samenvatting

---

## 2. Fase 2 Docker Stack - ✅ AFGEROND

**Wat is geïmplementeerd:**
- ✅ Modulaire orchestrator met Protocol-based services (SOLID)
- ✅ Docker Compose met 4 services: Ollama, Voxtral, TTS, Orchestrator
- ✅ Alle services healthy met werkende health checks
- ✅ /chat endpoint (text → LLM → response)
- ✅ /audio-conversation endpoint (audio → STT → LLM → TTS → audio)
- ✅ TTS checkpoints verplaatst naar fase2-refactor/tts/fishaudio/
- ✅ TTS cache volume voor snellere restarts
- ✅ Dutch2 reference audio correct geconfigureerd

**Stack starten:**
```bash
cd fase2-refactor
docker compose up -d
```

**Testen:**
```bash
# Health check
curl http://localhost:8200/health

# Audio pipeline
curl -X POST http://localhost:8200/audio-conversation \
  -F "audio=@test.wav" --output response.wav
aplay response.wav
```

Zie: [`fase2-refactor/PLAN.md`](fase2-refactor/PLAN.md)

---

## 3. WebSocket Testen → TODO

**Doel:**
- WebSocket endpoint testen zonder Pi (met wscat of Python script)
- AUDIO_PROCESS message flow valideren

---

## 4. VAD op Pi + Pipeline Test Script → Gepland Fase 3

**Huidige situatie Pi:**
- PiCar-X gebouwd en basis getest
- Standaard hardware config
- Nog GEEN: OLED scherm, Camera Module 3, ToF sensors, extra LEDs
- WEL aanwezig: mic (USB), speaker (I2S)

**Doel (Fase 2):**
1. VAD werkend krijgen op de Pi
2. Script maken om LLM pipeline te testen
3. Test: praten via car mic → desktop processing → antwoord via car speaker

---

## 5. OLED Aansluiten + Emotion Features → Gepland Fase 3

**Huidige situatie:**
- OLED WPI438 (SSD1306) aanwezig
- Nog niet aangesloten

**Doel (Fase 2/3):**
- OLED aansluiten op I2C bus
- Test met luma.oled
- Emotion display integreren met orchestrator responses

---

## Volgende Stappen

- **Fase 2**: Code cleanup, dockerizen, Pi integratie voorbereiden
- **Wachten op hardware**: Camera Module 3, ToF sensors, LEDs
- **Fase 3**: Hardware aansluiten, YOLO safety layer
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
