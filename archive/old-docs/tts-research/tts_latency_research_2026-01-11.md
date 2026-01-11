# TTS Latency Research - Alternatieven voor Chatterbox

**Datum:** 2026-01-11
**Aanleiding:** Chatterbox Multilingual latency 5-20 sec is te hoog voor real-time conversatie
**Doel:** Snellere TTS (<500ms) met acceptabele Nederlandse kwaliteit

---

## Huidige Situatie

### Chatterbox Multilingual (huidige implementatie)
- **Latency:** 5-20 seconden (gemeten)
- **Kwaliteit:** Goed, natuurlijke intonatie
- **Probleem:** Te traag voor real-time conversatie (Diffusion architectuur)

### Chatterbox Turbo - NIET BRUIKBAAR
**Gecontroleerd in code:** `tts_turbo.py` gebruikt `EnTokenizer` = **Engels only**
- Geen `language_id` parameter
- Ondersteunt GEEN Nederlands
- Perplexity claim over "Chatterbox Turbo ~300ms met NL" is **INCORRECT**

---

## Onderzochte Alternatieven

### ❌ StyleTTS2 / MeloTTS - AFGEWEZEN

**Reden:** Ondersteunt GEEN Nederlands out-of-the-box.

- "Multilingual" claims slaan op ES, FR, JA, KO, ZH - niet NL
- Zou zelf finetunen vereisen of obscure community fork
- Geen kant-en-klaar NL model beschikbaar

**Conclusie:** Niet beschikbaar voor Nederlands.

---

### ❌ Chatterbox Turbo - AFGEWEZEN

**Reden:** Engels only (`EnTokenizer`)
- Geen Nederlandse ondersteuning
- Code check bevestigt: geen `language_id` parameter

---

### ⭐ Optie 1: Mimic 3 - TE TESTEN

**Architectuur:** VITS (zoals Piper, maar beter getraind)
**Latency:** <100ms
**Docker:** `mycroftai/mimic3`

**Nederlandse stemmen:**
- **`nl_rdh` (Bart)** - Community favoriet
- **`FlemishGuy`** - Alternatieve stem

**Waarom potentieel beter dan Piper:**
- Zelfde VITS architectuur
- Anders/beter getrainde stemmodellen
- Mogelijk minder robotisch

**Test:**
- Zoek audio voorbeelden online
- Docker: `docker pull mycroftai/mimic3`

---

### ⭐ Optie 2: Sherpa-ONNX + vits-mms-nld - TE TESTEN

**Architectuur:** VITS (Facebook MMS project)
**Latency:** <50ms (snelste die bestaat)
**Model:** `vits-mms-nld` van HuggingFace

**Waarom interessant:**
- Meta's Massively Multilingual Speech project
- VITS getraind door Meta - mogelijk beter dan Piper
- Sherpa-ONNX = snelste inference engine

**Links:**
- Model: https://huggingface.co/facebook/mms-tts-nld
- Engine: https://github.com/k2-fsa/sherpa-onnx

---

### ❌ F5-TTS - AFGEWEZEN

**Reden:** Diffusion architectuur = inherent traag (~1s minimum)

---

### ❌ Piper - LAATSTE REDMIDDEL

**Latency:** <50ms
**Kwaliteit:** Robotisch, "blikkerig"

Alleen als NIETS anders werkt.

---

## Vergelijkingstabel

| Model | Latency | NL Support | Kwaliteit | Status |
|-------|---------|------------|-----------|--------|
| **Mimic 3 (nl_rdh)** | <100ms | ✅ Ja | ? Testen | **TE TESTEN** |
| **Sherpa-ONNX (mms)** | <50ms | ✅ Ja | ? Testen | **TE TESTEN** |
| Chatterbox Multilingual | 5-20s | ✅ Ja | ⭐⭐⭐⭐ Goed | Huidige (te traag) |
| Chatterbox Turbo | - | ❌ Nee | - | Engels only |
| StyleTTS2 | - | ❌ Nee | - | Niet beschikbaar |
| F5-TTS | ~1s | ✅ Ja | ⭐⭐⭐⭐ | Te traag |
| Piper | <50ms | ✅ Ja | ⭐ Robotisch | Laatste redmiddel |

---

## Actieplan

### Stap 1: Audio voorbeelden zoeken
1. Mimic 3 Nederlandse stemmen - YouTube/demo's
2. Sherpa-ONNX MMS NL samples - HuggingFace

### Stap 2: Beste optie implementeren en testen
1. Latency meten
2. Kwaliteit beoordelen
3. Vergelijken met Chatterbox

### Stap 3: Beslissing
- Acceptabele kwaliteit + lage latency > perfecte kwaliteit + hoge latency
- Robot use-case: enige "digitale assistent" klank mogelijk acceptabel

---

## Conclusie

Er zijn **twee realistische opties** voor snelle lokale Nederlandse TTS:

1. **Mimic 3** - VITS met betere training dan Piper
2. **Sherpa-ONNX + MMS** - Meta's multilingual VITS

Beide moeten getest worden op kwaliteit. Chatterbox (Multilingual) blijft als fallback.

---

## Referenties

- [Mimic 3 Voices](https://github.com/MycroftAI/mimic3-voices)
- [Facebook MMS-TTS-NLD](https://huggingface.co/facebook/mms-tts-nld)
- [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx)
- Chatterbox code check: `tts_turbo.py` lijn 18 - `EnTokenizer` (Engels only)

---

*Onderzoek bijgewerkt: 2026-01-11*
