# Fase 1: Desktop Pipeline - AFGEROND ✅

**Datum:** 2026-01-16
**Status:** ✅ AFGEROND

---

## Overzicht

| # | Issue | Status | Opmerking |
|---|-------|--------|-----------|
| 1 | TTS klinkt soms Engelserig | ✅ Verbeterd | Prompt + normalisatie |
| 2 | Text normalisatie | ✅ Geïmplementeerd | Acroniemen, getallen, haakjes |
| 3 | Temperature/top_p tuning | ✅ Getest | temp=0.5, top_p=0.6 |
| 4 | Langere reference audio | ✅ Geïmplementeerd | 30s ElevenLabs reference |
| 5 | Prosody/expressie markers | ⏭️ Overgeslagen | Werkt niet met Fish Audio light |
| 6 | Pseudo-streaming | ✅ Geïmplementeerd | TTS per zin, ~3x snellere perceived latency |
| 7 | Playback interrupt | ✅ Geïmplementeerd | Spatiebalk in streaming mode |

---

## Samenvatting Implementaties

### 1. TTS Nederlandse Uitspraak
**Status:** ✅ Verbeterd (niet perfect)

**Gedaan:**
- System prompt aangepast: korte antwoorden (1-3 zinnen), geen markdown
- Robot capabilities en beperkingen in prompt
- Nederlandse woordvoorkeur

**Bekende beperkingen:**
- Sommige woorden klinken nog Engels ("herkent" → "herke")
- Vraagintonatie niet altijd correct
- Dit is een Fish Audio limitatie, niet op te lossen zonder andere TTS

---

### 2. Text Normalisatie
**Status:** ✅ Geïmplementeerd

**Functionaliteit:**
- Acroniemen → Nederlandse fonetiek: "API" → "aa-pee-ie", "ASML" → "aa-es-em-el"
- Getallen → woorden: "247" → "tweehonderdzevenenveertig"
- Haakjes → eerste `(` wordt komma, rest verwijderd
- Specifieke woorden: "Docker" → "dokker"

**Bestanden:**
- `orchestrator/main.py` - `normalize_for_tts()` functie
- `vad_conversation.py` - toont genormaliseerde tekst

---

### 3. Temperature/Top_p Tuning
**Status:** ✅ Getest en geconfigureerd

**Huidige waarden (met 30s reference):**
```yaml
temperature: 0.5
top_p: 0.6
```

**Test resultaten:**
- temp=0.2, top_p=0.5 → te saai, monotoon
- temp=0.3, top_p=0.6 → meer leven, maar uitspraak slechter
- temp=0.4, top_p=0.55 → beste compromis (oude 10s reference)
- temp=0.5, top_p=0.6 → test met nieuwe 30s reference (huidige)

---

### 4. Langere Reference Audio
**Status:** ✅ Geïmplementeerd

**Nieuwe reference:**
```
original_fish-speech-REFERENCE/references/dutch2/
├── reference.mp3   # 30 seconden, ~508KB
└── reference.lab   # Transcriptie met emoties
```

**Reference tekst (ElevenLabs gegenereerd):**
```
Hallo, wat fijn dat je er bent! Ik ben zo blij vandaag!
Ken je die Nederlandse machines van ASML? Ik ben nieuwsgierig wat jij daarvan vindt.
Soms voel ik me een beetje verdrietig, vooral als het lang stil blijft, dan kan ik wel janken.
Maar dit maakt me echt BOOS, ik mep je in elkaar hufter!!
Gelukkig herken ik jou via de camera, zelfs bij vijftien anderen.
Schouder, ijsberg, eeuwige gezelligheid.
```

**Bevat:**
- Alle emoties: blij, nieuwsgierig, verdrietig, boos
- Probleemwoorden: machines, Nederlandse, ASML, herkent
- Moeilijke klanken: sch, ui, eu, ij, g/ch

---

### 5. Prosody/Expressie Markers
**Status:** ⏭️ Overgeslagen

**Reden:** Emotie markers zoals `(happy)`, `(sad)` werken niet met Fish Audio's lokale model voor Nederlands. Taal-agnostische markers (`(laughing)`, `(whispering)`) zijn niet getest maar waarschijnlijk inconsistent.

**Alternatief:** Modulaire TTS architectuur maakt toekomstige switch naar ElevenLabs API mogelijk.

---

### 6. Pseudo-Streaming (Per Zin)
**Status:** ✅ Geïmplementeerd

**Hoe het werkt:**
1. LLM genereert volledige response
2. Response wordt gesplitst in zinnen
3. TTS genereert audio per zin via SSE stream
4. Audio wordt direct afgespeeld terwijl volgende zin TTS draait

**Voordeel:**
- Batch mode: wacht op TTS van alle zinnen (~3s) → dan afspelen
- Streaming mode: wacht op TTS van 1 zin (~600ms) → direct afspelen
- **~3x snellere perceived latency**

**Configuratie:**
```yaml
tts:
  streaming: true  # false = batch, true = streaming
```

**Bestanden:**
- `orchestrator/main.py` - `/conversation/streaming` endpoint met SSE
- `vad_conversation.py` - streaming client met timing breakdown

---

### 7. Playback Interrupt
**Status:** ✅ Geïmplementeerd (desktop)

**Functionaliteit:**
- Spatiebalk onderbreekt audio playback
- Werkt alleen in streaming mode
- Terminal settings worden correct hersteld bij Ctrl+C

**Later (Pi hardware):**
- Fysieke knop of gebaar detectie aanbevolen
- Voice interrupt complex door echo probleem

---

## Bekende Beperkingen (Acceptabel)

| Issue | Status | Opmerking |
|-------|--------|-----------|
| Sommige woorden Engels | Acceptabel | Fish Audio limitatie |
| Vraagintonatie niet altijd goed | Acceptabel | Model limitatie |
| Kleine pauzes tussen zinnen (streaming) | Acceptabel | Trade-off voor snelheid |

---

## Fase 1 Conclusie

**Desktop pipeline is volledig functioneel:**
- ✅ VAD → STT (Voxtral) → LLM (Ministral) → TTS (Fish Audio) → Speaker
- ✅ Conversation history met emotie state
- ✅ Function calling (show_emotion, take_photo)
- ✅ Text normalisatie voor betere NL uitspraak
- ✅ Pseudo-streaming voor snellere response
- ✅ Spatiebalk interrupt

**Klaar voor Fase 2:** Pipeline testen op Raspberry Pi 5
