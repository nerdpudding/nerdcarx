# Fase 1: Openstaande Punten

**Datum:** 2026-01-11
**Status:** Plan voor review

---

## Overzicht

| # | Issue | Prioriteit | Status |
|---|-------|------------|--------|
| 1 | TTS klinkt soms Engelserig | Hoog | Onderzoeken |
| 2 | Text normalisatie (nieuw!) | Hoog | Implementeren |
| 3 | Temperature/top_p tuning | Hoog | Testen |
| 4 | Langere reference audio | Medium | Optioneel |
| 5 | Prosody/expressie markers | Laag | Optioneel |
| 6 | Snellere audio response | Laag | Pseudo-streaming |
| 7 | Playback interrupt | Laag | Spatiebalk |

**Verwijderd uit plan (niet meer van toepassing):**
- ~~VRAM memory leak~~ - Geen issue bij Fish Audio
- ~~Voxtral NL taal~~ - Al gedaan (`language: 'nl'` in vad_conversation.py:110)
- ~~Context sliding window~~ - Geen actueel probleem
- ~~Noise removal~~ - ElevenLabs audio is al clean
- ~~Korte zinnen~~ - Lengte is geen probleem voor latency

---

## 1. TTS Klinkt Soms Engelserig

### Probleem
Via orchestrator klinkt TTS soms met Engels accent, terwijl standalone tests goed klinken.

### Mogelijke oorzaak
LLM gebruikt soms Engelse woorden/zinstructuren die TTS beïnvloeden.

### Aanbevolen actie

**Optie A: Prompt toevoegen** (5 min)
```yaml
# config.yml - toevoegen aan system_prompt
Gebruik bij voorkeur Nederlandse woorden. Vermijd onnodige Engelse termen.
```

**Optie B: Temperature/top_p tuning** (zie punt 2)

**Optie C: Langere reference audio** (zie punt 3)

**Optie D: Fine-tuning** (voor later, 2-4 uur)
- ~30 min NL audio met transcripties
- Training: 1-2 uur op RTX 4090
- Overwegen als A, B en C niet voldoende helpen

### Debug tip
Log exact de tekst die naar TTS gaat en vergelijk met standalone tests:
```python
# orchestrator/main.py - synthesize_speech()
print(f"[TTS INPUT] {text}")  # Voeg toe voor debugging
```

---

## 2. Text Normalisatie (NIEUW)

### Waarom dit belangrijk is
De TTS spreekt uit wat er letterlijk staat. Als de LLM "API" of "150" schrijft,
probeert Fish Audio dat als Engels/internationaal uit te spreken → klinkt Engelserig.

**Dit is vaak effectiever dan langere reference audio!**

### Wat normaliseren?

| Input | Probleem | Genormaliseerd |
|-------|----------|----------------|
| API | Klinkt Engels | aa-pee-ie |
| USB | Klinkt Engels | joe-es-bee |
| GPU | Klinkt Engels | zjee-pee-joe |
| Docker | Klinkt Engels | dokker |
| 150 | Onduidelijk | honderdvijftig |
| 2.5 | Onduidelijk | twee komma vijf |
| RTX 4090 | Mix Engels/cijfers | er-tee-ex veertig negentig |

### Implementatie (robuuste versie)

```python
# orchestrator/main.py - nieuwe functie
import re
from num2words import num2words  # pip install num2words

def normalize_for_tts(text: str) -> str:
    """Normaliseer tekst voor betere Nederlandse TTS uitspraak."""

    # 1. ACRONIEMEN: letter-voor-letter uitspreken
    #    Dekt automatisch API, USB, GPU, HTTP, JSON, VRAM, MCP, etc.
    NL_LETTER_SOUNDS = {
        'A': 'aa', 'B': 'bee', 'C': 'see', 'D': 'dee', 'E': 'ee',
        'F': 'ef', 'G': 'zjee', 'H': 'haa', 'I': 'ie', 'J': 'jee',
        'K': 'kaa', 'L': 'el', 'M': 'em', 'N': 'en', 'O': 'oo',
        'P': 'pee', 'Q': 'kuu', 'R': 'er', 'S': 'es', 'T': 'tee',
        'U': 'uu', 'V': 'vee', 'W': 'wee', 'X': 'iks', 'Y': 'ei',
        'Z': 'zet'
    }

    def spell_acronym(match):
        acronym = match.group(0)
        return '-'.join(NL_LETTER_SOUNDS.get(c, c) for c in acronym)

    # Match 2+ hoofdletters als heel woord (word boundaries)
    text = re.sub(r'\b[A-Z]{2,}\b', spell_acronym, text)

    # 2. SPECIFIEKE WOORDEN: case-insensitive met word boundaries
    word_replacements = {
        r'\bDocker\b': 'dokker',
        r'\bPython\b': 'paiton',
        r'\bLinux\b': 'Linux',  # klinkt al ok
        r'\bNerdCarX\b': 'NerdCarX',  # eigen naam
    }
    for pattern, replacement in word_replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 3. GETALLEN: naar Nederlandse woorden
    def replace_number(match):
        num_str = match.group(0)
        try:
            # Decimalen: "2.5" → "twee komma vijf"
            if '.' in num_str:
                parts = num_str.split('.')
                whole = num2words(int(parts[0]), lang='nl')
                decimal = ' '.join(num2words(int(d), lang='nl') for d in parts[1])
                return f"{whole} komma {decimal}"
            # Ranges: "3-5" → "drie tot vijf"
            if '-' in num_str and num_str.count('-') == 1:
                parts = num_str.split('-')
                return f"{num2words(int(parts[0]), lang='nl')} tot {num2words(int(parts[1]), lang='nl')}"
            # Gewone getallen
            return num2words(int(num_str), lang='nl')
        except:
            return num_str

    # Match getallen (inclusief decimalen en ranges)
    text = re.sub(r'\b\d+(?:\.\d+)?(?:-\d+)?\b', replace_number, text)

    return text

# Gebruik in synthesize_speech():
text = normalize_for_tts(text)
```

### Wat deze versie doet

| Input | Output | Hoe |
|-------|--------|-----|
| API | aa-pee-ie | Automatisch: 2+ hoofdletters |
| HTTP | haa-tee-tee-pee | Automatisch: 2+ hoofdletters |
| Docker | dokker | Specifieke vervanging |
| 150 | honderdvijftig | num2words |
| 2.5 | twee komma vijf | Decimaal herkenning |
| 3-5 | drie tot vijf | Range herkenning |

### Prioriteit
**Hoog** - Probeer dit VOOR je aan reference audio gaat sleutelen.

### Dependencies
```bash
pip install num2words
```

---

## 3. Temperature/Top_p Tuning

### Achtergrond
Fish Audio parameters:
- `temperature` = variation (lager = voorspelbaarder, hoger = expressiever)
- `top_p` = diversity (lager = gefocust, hoger = diverser)

**Hoger zetten** = meer levendigheid, maar ook meer kans op rare prosody/uitspraak.
Bij NL kan dat sneller "Engels-achtig" uitpakken.

### Huidige waarden
```yaml
temperature: 0.2   # ultra_consistent
top_p: 0.5         # ultra_consistent
```

### Test aanpak (stap voor stap)

**Waarom deze volgorde:** Huidige 0.2/0.5 is zó conservatief dat je snel "saai" concludeert.
Beter: **eerst top_p variëren, dan temperature**.

#### Stap 1: Varieer alleen top_p (houd temperature=0.3)

| Test | temperature | top_p | Verwacht effect |
|------|-------------|-------|-----------------|
| A | 0.3 | 0.5 | Baseline (iets minder saai dan 0.2) |
| B | 0.3 | 0.6 | Iets meer leven |
| C | 0.3 | 0.7 | Meer diversiteit, nog stabiel |

**Stop zodra je tevreden bent.** Meestal is 0.6-0.7 al genoeg.

#### Stap 2: Varieer temperature (met beste top_p van stap 1)

| Test | temperature | top_p | Verwacht effect |
|------|-------------|-------|-----------------|
| D | 0.45 | [beste] | Iets meer "kleur" |
| E | 0.6 | [beste] | Expressiever |
| F | 0.7 | [beste] | Levendig (mogelijk te veel) |

**Stop zodra uitspraak slechter wordt.** Daar zit je sweet spot.

### Samenvatting

```
Start: temp=0.3, top_p=0.5
  ↓
Verhoog top_p tot je "leven" hoort (meestal 0.6-0.7)
  ↓
Verhoog temperature tot uitspraak slechter wordt
  ↓
Sweet spot gevonden!
```

### Aanbeveling
Als "saai" maar uitspraak moet strak blijven: verhoog eerst `top_p` licht (0.5 → 0.7) en laat `temperature` lager (0.3–0.5).

---

## 4. Langere Reference Audio

### Onze huidige setup

**Reference locatie:**
```
original_fish-speech-REFERENCE/references/dutch2/
├── reference.mp3   # Audio (~10 seconden, 174KB)
└── reference.lab   # Transcriptie tekst
```

**Reference tekst:**
```
Hallo, welkom! Ik ben NerdCarX, je persoonlijke assistent.
Vandaag is het prachtig weer, vind je niet?
Ik zie twee honden spelen in het park. Zal ik je ergens mee helpen?
```

**Bron:** ElevenLabs Nederlandse vrouwenstem

### Hoe caching werkt

Wij gebruiken de **HTTP API** (niet command line), dus caching werkt automatisch:

| Methode | Caching mechanisme | Onze situatie |
|---------|-------------------|---------------|
| Command line | `fake.npy` bestand (handmatig) | Niet van toepassing |
| HTTP API | In-memory via `ReferenceLoader` | **Dit gebruiken wij** ✅ |

**Fish Audio `ReferenceLoader` (reference_loader.py:52-72):**
```python
if use_cache == "off" or id not in self.ref_by_id:
    # Encode reference audio naar tokens (éénmalig bij eerste request)
    prompt_tokens = [self.encode_reference(...) for ref_audio in ref_audios]
    self.ref_by_id[id] = (prompt_tokens, prompt_texts)  # Cache in-memory
else:
    # Hergebruik cached tokens (alle volgende requests)
    logger.info("Use same references")
    prompt_tokens, prompt_texts = self.ref_by_id[id]
```

**Resultaat:**
- Eerste TTS request: encodeert `dutch2` reference (~10s audio → tokens)
- Alle volgende requests: hergebruikt cached tokens uit `self.ref_by_id["dutch2"]`
- **Geen latency impact** bij langere reference (encoding is éénmalig)

### Huidige reference beoordeling

| Aspect | Status | Opmerking |
|--------|--------|-----------|
| Lengte | ✅ ~10s | Fish Audio adviseert 10-20s |
| Variatie | ⚠️ Beperkt | Geen vraagzin, cijfers, afkortingen |
| Kwaliteit | ✅ Goed | ElevenLabs bron |

### Optioneel: "NL Torture Test" Reference

Als NL uitspraak niet goed genoeg is, maak een uitgebreide reference (15-20 seconden) die alle lastige Nederlandse klanken bevat:

**Voorbeeld tekst voor nieuwe reference:**
```
Hallo, welkom bij NerdCarX! Ik ben je persoonlijke assistent.

Vandaag is het prachtig weer, vind je niet? De temperatuur is ongeveer
vijftien graden. Ik kan je helpen met allerlei taken.

Wil je dat ik een foto maak? Of zal ik je iets vertellen over
technologie? Ik weet veel over aa-pee-ie's, joe-es-bee poorten,
en andere dingen.

Mijn favoriete Nederlandse woorden zijn: schouder, eeuwig, ijsberg,
en natuurlijk gezelligheid!
```

**Checklist voor goede reference:**
- [ ] Moeilijke NL klanken: "sch", "ui", "eu", "ij"
- [ ] Minstens 1 vraagzin (stijgende intonatie)
- [ ] Minstens 1 uitroep (emotie)
- [ ] Getallen in woorden ("vijftien", "honderdvijftig")
- [ ] Afkortingen uitgesproken zoals gewenst ("aa-pee-ie")
- [ ] Neutrale zinnen (baseline)
- [ ] Korte pauzes tussen zinnen

### Actie (indien nodig)
1. Genereer tekst hierboven via ElevenLabs (Nederlandse stem)
2. Plaats audio in `references/dutch3/sample.mp3`
3. Maak `references/dutch3/sample.lab` met dezelfde tekst
4. Update `config.yml`: `reference_id: "dutch3"`
5. Test of NL uitspraak verbetert
6. Als beter: verwijder oude `dutch2`

---

## 5. Prosody/Expressie Markers (optioneel)

### Analyse
Perplexity beweert dat emotie markers niet werken voor Nederlands. Maar:
- `(happy)`, `(sad)`, `(excited)` → **Werken NIET voor NL**
- `(laughing)`, `(whispering)`, `(sighing)`, `(chuckling)` → **Taal-agnostisch, kunnen werken**

### Implementatie (indien gewenst)
```python
# orchestrator/main.py - synthesize_speech()
EMOTION_PROSODY = {
    "happy": "(chuckling)",
    "excited": "(laughing)",
    "shy": "(whispering)",
    "sad": "(sighing)",
}

prosody = EMOTION_PROSODY.get(emotion, "")
text = f"{prosody} {text}" if prosody else text
```

### Aanbeveling
Laag prioriteit. Test eerst of deze markers überhaupt effect hebben.

---

## 6. Snellere Audio Response (Streaming Opties)

### Het probleem begrijpen

**Huidige situatie:**
```
Gebruiker zegt iets
    ↓
LLM genereert HELE antwoord (bv. 3 zinnen)     → 1 seconde
    ↓
TTS maakt audio van HELE antwoord              → 1.2 seconde
    ↓
Audio wordt afgespeeld                          → 3 seconden
────────────────────────────────────────────────
Totale wachttijd voor gebruiker: ~2.2 seconden
```

**Wat we willen:**
De gebruiker hoort al iets terwijl de rest nog wordt gemaakt.

---

### De 3 opties uitgelegd

#### Optie 1: Hoe het nu werkt (Volledig wachten)
```
[LLM maakt alles] → [TTS maakt alles] → [Afspelen]
```

| Voordeel | Nadeel |
|----------|--------|
| Simpel, werkt betrouwbaar | Gebruiker wacht op alles |
| Geen technische complexiteit | Voelt traag aan |

**Status:** Dit hebben we nu. Werkt prima voor korte antwoorden.

---

#### Optie 2: Pseudo-streaming (Per zin) ⭐ AANBEVOLEN

```
LLM maakt zin 1 → TTS maakt zin 1 → Afspelen zin 1
                  LLM maakt zin 2 → TTS maakt zin 2 → Afspelen zin 2
                                    LLM maakt zin 3 → ...
```

**Hoe het werkt:**
1. LLM genereert tekst
2. Orchestrator splitst op zinnen (bij `. ` of `! ` of `? `)
3. Eerste zin → TTS → direct naar Pi/speaker
4. Ondertussen: volgende zin → TTS → sturen
5. Gebruiker hoort continu audio

| Voordeel | Nadeel |
|----------|--------|
| Gebruiker hoort sneller iets | Iets meer code nodig |
| Werkt met onze huidige setup | Kleine pauzes tussen zinnen mogelijk |
| Geen speciale libraries nodig | |
| Perfect voor Pi ↔ Desktop over WiFi | |

**Waarom dit de beste optie is voor ons:**
- Werkt met onze bestaande HTTP `/v1/tts` endpoint
- Geen websocket/SDK nodig
- Past perfect bij Pi → Desktop over thuisnetwerk
- Gebruiker hoort eerste zin na ~1s ipv na ~2.2s

---

#### Optie 3: Echte streaming (WebSocket)

```
[Audio bytes komen binnen als stroom] → [Direct afspelen]
```

**Hoe het zou werken:**
- WebSocket verbinding met TTS server
- Audio bytes komen "live" binnen terwijl TTS nog bezig is
- Direct afspelen zonder te wachten op hele audio

| Voordeel | Nadeel |
|----------|--------|
| Allersnelste mogelijke response | WebSocket is voor Fish Audio CLOUD SDK |
| Professionele UX | Lokale fish-speech server ondersteunt dit NIET goed |
| | HTTP `stream=true` geeft vaak ruis/klikken |
| | Complexe implementatie |

**Waarom dit NIET voor ons werkt:**
- Fish Audio WebSocket (`stream_websocket`) is voor hun **cloud API/SDK**
- Onze lokale fish-speech Docker heeft geen betrouwbare streaming
- Eerdere test met `stream=true` gaf ruis (audio chunks zijn "netwerk pakketjes", geen nette audio blokken)

---

### Samenvatting: Welke optie kiezen?

| Optie | Geschikt voor ons? | Reden |
|-------|-------------------|-------|
| 1. Volledig wachten | ✅ Nu | Werkt, simpel |
| 2. Pseudo-streaming | ⭐ Beste upgrade | Werkt met onze setup, snellere UX |
| 3. WebSocket streaming | ❌ Nee | Alleen voor cloud, niet lokaal |

---

### Implementatie pseudo-streaming (optie 2)

#### Basis versie

```python
# orchestrator/main.py - nieuwe aanpak

def split_into_sentences(text: str) -> list[str]:
    """Split tekst in zinnen."""
    import re
    # Split op . ! ? gevolgd door spatie of einde
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

async def process_with_pseudo_streaming(llm_response: str, client):
    """Genereer en stuur audio per zin."""
    sentences = split_into_sentences(llm_response)

    for sentence in sentences:
        # TTS voor deze zin
        audio = await synthesize_speech(sentence, emotion, client)

        # Direct sturen naar client/Pi (niet wachten op rest)
        yield audio
```

#### Verbeteringen voor "chat feel"

**1. LLM → TTS Pipelining:**
Start TTS zodra je een zin-einde detecteert, terwijl LLM doorgaat:

```python
import asyncio

async def pipeline_tts(llm_stream, client):
    """Pipeline: detecteer zin-einde, start TTS terwijl LLM doorgaat."""
    buffer = ""

    async for chunk in llm_stream:
        buffer += chunk

        # Check op zin-einde
        while any(end in buffer for end in ['. ', '! ', '? ']):
            # Vind eerste zin-einde
            for end in ['. ', '! ', '? ']:
                if end in buffer:
                    idx = buffer.index(end) + 1
                    sentence = buffer[:idx].strip()
                    buffer = buffer[idx:].strip()

                    # Start TTS voor deze zin (async, niet blokkeren)
                    yield sentence
                    break

    # Laatste zin (zonder einde-punctuatie)
    if buffer.strip():
        yield buffer.strip()
```

**2. Micro-buffering (playback kant):**
Buffer kort (150-300ms) voordat je begint af te spelen → voorkomt "gaten" door netwerk-jitter:

```python
# vad_conversation.py of Pi client
import asyncio

async def play_with_buffer(audio_stream, buffer_ms=200):
    """Buffer audio kort voor smooth playback."""
    buffer = []
    buffer_size = int(24000 * buffer_ms / 1000)  # samples @ 24kHz

    async for audio_chunk in audio_stream:
        buffer.append(audio_chunk)
        total_samples = sum(len(c) for c in buffer)

        # Start pas afspelen als buffer vol genoeg is
        if total_samples >= buffer_size:
            # Play eerste chunk, blijf bufferen
            play_audio(buffer.pop(0))

    # Speel resterende buffer af
    for chunk in buffer:
        play_audio(chunk)
```

### Wanneer implementeren?

| Versie | Complexiteit | Wanneer |
|--------|--------------|---------|
| Basis (per zin) | Laag | Als huidige latency stoort |
| + Pipelining | Medium | Voor langere antwoorden |
| + Micro-buffering | Medium | Als je "gaten" hoort over WiFi |

Huidige ~1.2s is acceptabel. Overweeg voor fase 2/3.

---

## 7. Playback Interrupt

### Oplossing: Spatiebalk (desktop)

```python
# vad_conversation.py - play_audio()
import threading

stop_event = threading.Event()

def keyboard_listener():
    import keyboard
    keyboard.wait('space')
    stop_event.set()

thread = threading.Thread(target=keyboard_listener, daemon=True)
thread.start()

# In playback loop: check stop_event.is_set()
```

### Later (hardware)
Als Pi hardware komt, andere oplossing nodig (wake word, button, etc.).

---

## Volgorde van Aanpak

| # | Actie | Tijd | Prioriteit |
|---|-------|------|------------|
| 1 | Prompt aanpassen (Engelse termen) | 5 min | Hoog |
| 2 | Text normalisatie implementeren | 30 min | Hoog |
| 3 | Temperature/top_p test grid | 30 min | Hoog |
| 4 | Langere reference audio | 30 min | Medium |
| 5 | Spatiebalk interrupt | 30 min | Laag |
| 6 | Prosody markers testen | 15 min | Laag |
| 7 | Pseudo-streaming per zin | 1-2 uur | Later |

**Totaal voor 1-5:** ~2 uur

---

## Bestanden

| Wijziging | Bestand |
|-----------|---------|
| Prompt Engelse termen | `config.yml` |
| Text normalisatie | `orchestrator/main.py` (nieuwe functie) |
| Temperature/top_p | `config.yml` |
| Reference audio | `original_fish-speech-REFERENCE/references/dutch3/` |
| Prosody markers | `orchestrator/main.py` |
| Playback interrupt | `vad-desktop/vad_conversation.py` |
| Pseudo-streaming | `orchestrator/main.py` (refactor) |

---

## Verificatie

Na wijzigingen:
1. Start conversatie
2. Luister of TTS Nederlandser klinkt
3. Vergelijk expressie bij verschillende temp/top_p
4. Test spatiebalk interrupt (als geïmplementeerd)
