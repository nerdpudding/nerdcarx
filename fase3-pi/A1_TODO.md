# A1: pi_conversation_v2 - Uitgebreide Debug Info

**Datum:** 2026-01-17
**Doel:** Desktop-achtige conversatie ervaring op Pi met volledige debug output

---

## Wat willen we?

Een verbeterde versie van `pi_conversation.py` die:

1. **Wake word slechts 1x** - Bij start, daarna gewoon VAD-based zoals desktop
2. **Desktop-achtige debug output**:
   - Timing per stap (STT, LLM, TTS)
   - Tool calls weergave met details
   - Emotie state changes met emoji's
   - Text normalisatie weergave
   - Turn summary
3. **Mock function call handling** - Zodat we flow kunnen testen zonder echte hardware
4. **Makkelijk uit te breiden** - Voor later als camera/OLED werkend zijn

---

## Verschil v1 vs v2

| Aspect | v1 (huidige) | v2 (nieuw) |
|--------|--------------|------------|
| Wake word | Elke turn | Alleen bij start |
| Debug output | Minimaal | Uitgebreid (zoals desktop) |
| Timing | Geen | Per stap (STT, LLM, TTS) |
| Tool calls | Alleen print | Details + mock handling |
| Emoties | Niet weergegeven | Emoji's + state changes |
| Mock support | Nee | Ja (take_photo, show_emotion) |

---

## Taken

### Stap 1: Files voorbereiden
- [x] `pi_conversation.py` → `pi_conversation_v1.py` (hernoemen)
- [x] `pi_conversation_v2.py` aanmaken

### Stap 2: Test foto kopiëren naar Pi
- [x] Mock foto (`mock_photo.jpg`) beschikbaar maken op Pi

### Stap 3: v2 Features implementeren
- [x] Wake word alleen bij start
- [x] Na wake word: VAD-based conversation loop (zoals desktop)
- [x] Timing info per stap
- [x] Tool call weergave met details
- [x] Emotie emoji's en state tracking
- [x] Mock `take_photo` handling (return mock beschrijving)
- [x] Mock `show_emotion` handling (print naar console)
- [x] Turn summary aan einde

### Stap 4: Testen
- [x] Wake word trigger ✅
- [x] Eerste conversatie turn ✅
- [ ] Meerdere turns zonder wake word
- [ ] Emotie changes detecteren
- [ ] Mock take_photo trigger ("wat zie je?")

### Stap 5: Remote Tool Pattern (D016) - NIEUW
- [x] Protocol uitgebreid met FUNCTION_REQUEST en FUNCTION_RESULT
- [x] Tool base: is_remote property toegevoegd
- [x] VisionTool: is_remote=True gezet
- [x] Handler: remote tool logic geïmplementeerd
- [x] Pi client: FUNCTION_REQUEST handler toegevoegd
- [x] Docker containers rebuilt
- [ ] **Rsync naar Pi** (wacht op Pi herstel na batterij crash)
- [ ] **End-to-end test** take_photo via Pi

### Status: IMPLEMENTATIE COMPLEET, TEST PENDING (2026-01-17)
Remote Tool Pattern (D016) volledig geïmplementeerd:
- Desktop orchestrator stuurt nu FUNCTION_REQUEST voor remote tools
- Pi client handelt FUNCTION_REQUEST af en stuurt FUNCTION_RESULT terug
- Mock take_photo leest mock_photo.jpg en stuurt base64 naar orchestrator

**Nog te doen:**
1. Rsync naar Pi (na herstel van batterij crash)
2. End-to-end test uitvoeren (zie Testplan in Fase3_Implementation_Plan.md)

---

## Test Commando's

```bash
# Op desktop - zorg dat services draaien
cd ~/vibe_claude_kilo_cli_exp/nerdcarx/fase2-refactor
docker compose up -d
curl http://localhost:8200/health

# Op Pi
ssh 192.168.1.71
conda activate nerdcarx
cd ~/fase3-pi/test_scripts
python pi_conversation_v2.py
```

---

## Flow Diagram v2

```
[Start]
    │
    ▼
[Wake word luisteren] ─── "hey jarvis" ───┐
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                    CONVERSATION LOOP (VAD-based)                 │
│                                                                  │
│  [VAD luisteren] → [Opname] → [WebSocket] → [Play response]      │
│        │                                           │             │
│        └───────────────── volgende turn ───────────┘             │
│                                                                  │
│  (geen wake word nodig - net als desktop versie)                 │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
[Ctrl+C of "stop" commando] → [Exit]
```

---

## Mock Handling

### take_photo
Wanneer LLM `take_photo` aanroept:
1. Print "[MOCK] take_photo aangeroepen"
2. Return placeholder beschrijving: "Dit is een mock foto. Op de echte foto staan twee honden."
3. (Later: echte camera integratie)

### show_emotion
Wanneer LLM `show_emotion` aanroept:
1. Print emotie met emoji naar console
2. (Later: OLED display integratie)

---

## Referenties

- **Desktop versie:** `fase1-desktop/vad-desktop/vad_conversation.py`
- **Pi v1:** `fase3-pi/test_scripts/pi_conversation_v1.py`
- **Mock foto:** `fase3-pi/test_scripts/mock_photo.jpg`

---

## Voortgang

| Datum | Update |
|-------|--------|
| 2026-01-17 | A1_TODO aangemaakt |
| 2026-01-17 | v1 hernoemd, v2 aangemaakt |
| 2026-01-17 | Device detectie op naam geïmplementeerd |
| 2026-01-17 | Sample rate resampling toegevoegd (44.1kHz → 16kHz) |
| 2026-01-17 | Wake word + VAD werkend met resampling |
| 2026-01-17 | Emotion type bug gefixed, A1 volledig werkend |
| 2026-01-17 | **D016 Remote Tool Pattern geïmplementeerd** (protocol, handler, Pi client) |
| 2026-01-17 | Deadlock fix in websocket route (parallel receive loop) |
| 2026-01-17 | **END-TO-END TEST GESLAAGD** - take_photo werkt volledig |

---

## BELANGRIJKE BEVINDINGEN & ISSUES

### 1. Device Indices Veranderen Na Reboot!

**Probleem:** PyAudio device indices zijn niet stabiel. Na reboot of USB reconnect kunnen ze veranderen.

**Oplossing:** Zoek devices op **naam** in plaats van hardcoded index:
```python
MIC_DEVICE_NAME = "USB PnP Sound Device"
SPEAKER_DEVICE_NAME = "hifiberry"

# Zoek op naam met find_device_by_name()
mic_idx, mic_rate, mic_name = find_device_by_name(p, MIC_DEVICE_NAME, need_input=True)
```

### 2. Sample Rate Mismatch

**Probleem:** USB mic rapporteert 44100Hz als native rate, maar AI modellen verwachten 16000Hz.

**Oplossing:** Resample audio:
```python
MODEL_SAMPLE_RATE = 16000  # Wat modellen verwachten
MIC_SAMPLE_RATE = 44100    # Native mic rate (auto-gedetecteerd)

# Resample voor wake word / VAD / STT
if MIC_SAMPLE_RATE != MODEL_SAMPLE_RATE:
    audio_chunk = resample_audio(audio_chunk, MIC_SAMPLE_RATE, MODEL_SAMPLE_RATE)
```

### 3. ALSA/JACK Warnings Zijn Cosmetisch

**Probleem:** PyAudio geeft veel ALSA/JACK warnings bij initialisatie.

**Oplossing:** Negeren - ze zijn niet kritiek. Het script werkt gewoon.

```
ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM front
Cannot connect to server socket err = No such file or directory
jack server is not running or cannot be started
```

### 4. Emotion Response Format Varieert

**Probleem:** `emotion_info` van orchestrator is soms dict, soms string.

**Oplossing:** Check type voor gebruik:
```python
if isinstance(emotion_info, dict):
    emotion = emotion_info.get("current", "neutral")
else:
    emotion = emotion_info if emotion_info else "neutral"
```

### 5. Chunk Sizes Moeten Dynamisch Berekend Worden

**Probleem:** Hardcoded chunk sizes (1280, 480) zijn voor 16kHz. Bij 44.1kHz moet je omrekenen.

**Oplossing:** Bereken op basis van milliseconden:
```python
WAKE_CHUNK_MS = 80  # 80ms voor wake word
VAD_CHUNK_MS = 30   # 30ms voor VAD

mic_wake_chunk_size = int(MIC_SAMPLE_RATE * WAKE_CHUNK_MS / 1000)
mic_vad_chunk_size = int(MIC_SAMPLE_RATE * VAD_CHUNK_MS / 1000)
```

---

## Hardware Config Referentie (voor v1 compatibiliteit)

**Let op:** Deze indices kunnen veranderen! Altijd op naam zoeken.

| Component | PyAudio Name Pattern | Typische Index |
|-----------|---------------------|----------------|
| USB Mic | "USB PnP Sound Device" | 1 (was 2) |
| I2S Speaker | "hifiberry" | 0 (was 3) |
| GPIO Amplifier | GPIO 20 | n.v.t. |

**Sample rates:**
- Mic native: 44100Hz
- Model verwacht: 16000Hz
- Speaker: 44100Hz (TTS output is meestal 22050Hz of 44100Hz)
