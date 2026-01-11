# Full Flow Test - Fish Audio TTS Integratie

**Datum:** 2026-01-11
**Test:** VAD → STT → LLM → TTS → Speaker
**Conversation ID:** vad-9964b236

---

## Conclusies

### 1. Werkt ✅
De volledige flow werkt end-to-end met Fish Audio S1-mini als TTS.

### 2. Latency - Acceptabel ⚠️
| Component | Gemiddeld | Opmerkingen |
|-----------|-----------|-------------|
| STT | 150-280ms | Prima |
| LLM | 600-1100ms | Prima |
| TTS | 2200-3300ms | Acceptabel, niet geweldig |
| Playback | 12-20s | Afhankelijk van tekstlengte |
| **Totaal** | **15-25s** | Werkbaar maar niet ideaal |

**Actie voor later:** Streaming onderzoeken om TTS latency te verbeteren.

### 3. VRAM - Prima ✅
- Totaal in gebruik: ~17GB
- Betekent: Ruimte voor grotere LLM (14B model mogelijk)

### 4. TTS Kwaliteit - Kan Beter ⚠️

**Problemen:**
- Klinkt ENGELSER dan in de test scripts (`test_parameters.py`)
- Stem klinkt suffer/saaier, minder emotie
- Minder expressief dan de voorbeelden

**Mogelijke oorzaken:**
- Config parameters anders dan test script?
- Reference audio niet optimaal?
- Langere teksten → meer accent drift?

**Actie voor later:**
- [ ] Parameters vergelijken: config.yml vs test_parameters.py
- [ ] Andere reference audio proberen
- [ ] very_consistent vs ultra_consistent opnieuw vergelijken
- [ ] Kortere zinnen genereren in LLM prompt?

### 5. Tool Calls - Werkt ✅
Emotie tool calls werken correct:
- Turn 3: `show_emotion('worried')` ✅
- Turn 5: `show_emotion('confused')` ✅
- Turn 7: `take_photo(...)` ✅

### 6. STT Taal - Probleem ⚠️

Voxtral transcribeert soms Engels ipv Nederlands:
- Turn 4: "Now, and?" (was waarschijnlijk "Nou, en?")
- Turn 6: "We'll see you for you." (was waarschijnlijk "We zien wel" of iets dergelijks)

**Config check:** `language: 'nl'` IS correct ingesteld in `vad_conversation.py:110`

**Conclusie:** Voxtral negeert de language parameter soms. Dit is een bekend probleem met STT modellen - korte uitingen of onduidelijke audio wordt soms als Engels geïnterpreteerd.

**Mogelijke acties:**
- [ ] Voxtral prompt/instruction parameter toevoegen (indien ondersteund)
- [ ] Audio kwaliteit verbeteren (andere mic settings)
- [ ] Langere zinnen spreken helpt waarschijnlijk

---

## Test Data

### Timing per Turn

| Turn | STT | LLM | TTS | Playback | Totaal |
|------|-----|-----|-----|----------|--------|
| 1 | 126ms | 623ms | 2251ms | 12249ms | 15281ms |
| 2 | 184ms | 750ms | 2578ms | 14907ms | 18446ms |
| 3 | 204ms | 233ms | 0ms* | 0ms | 456ms |
| 4 | 123ms | 1011ms | 2712ms | 15647ms | 19521ms |
| 5 | 283ms | 1133ms | 3052ms | 18604ms | 23104ms |
| 6 | 155ms | 1020ms | 3219ms | 20441ms | 24867ms |
| 7 | 145ms | 4605ms** | 3272ms | 20509ms | 28563ms |

*Turn 3: Alleen tool call, geen tekst → geen TTS
**Turn 7: Vision call (take_photo) → extra latency

### Configuratie Gebruikt

```yaml
tts:
  url: "http://localhost:8250"
  reference_id: "dutch2"
  temperature: 0.2      # ultra_consistent
  top_p: 0.5            # ultra_consistent
  format: "wav"
```

---

## Vergelijking: Config vs Test Script

| Parameter | config.yml | test_parameters.py | Verschil? |
|-----------|------------|-------------------|-----------|
| reference_id | dutch2 | dutch2 | ✅ Gelijk |
| temperature | 0.2 | 0.2 | ✅ Gelijk |
| top_p | 0.5 | 0.5 | ✅ Gelijk |

**Conclusie:** Parameters zijn gelijk. Verschil in kwaliteit komt waarschijnlijk door:
- Langere zinnen (meer variatie/drift)
- Context van conversatie vs losse zinnen

---

## Audio Output

De TTS audio wordt opgeslagen in:
- **Locatie:** `fase1-desktop/vad-desktop/last_response.wav`
- **Gedrag:** Overschrijft elke turn - alleen de laatste response wordt bewaard
- **Bron:** `vad_conversation.py:33` definieert `RESPONSE_WAV`

---

## Feature Requests / Wensen

### 1. Playback Interrupt ⏸️

**Wens:** Playback kunnen onderbreken als NerdCarX te lang praat.

**Opties:**
- **Voice-based (ideaal):** Luisteren tijdens afspelen, VAD detecteert nieuwe spraak → stop playback
  - Uitdaging: Audio echo van speakers kan VAD triggeren
  - Oplossing: Noise cancellation of headphones
- **Keyboard-based:** Spatiebalk of ESC drukt stopt playback
  - Eenvoudiger te implementeren
- **Wake word:** Specifiek woord ("stop", "wacht") stopt playback

**Status:** Te implementeren in Fase 2 of later

---

## Volgende Stappen

1. [ ] Voxtral NL prompt checken en versterken
2. [ ] TTS streaming onderzoeken
3. [ ] 14B LLM model testen (VRAM beschikbaar)
4. [ ] TTS parameters fine-tunen voor langere teksten
5. [ ] Alternative reference audio testen
6. [ ] Playback interrupt implementeren

---

*Aangemaakt: 2026-01-11*
