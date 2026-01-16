# Fase 1: Openstaande Punten

**Datum:** 2026-01-16
**Status:** In uitvoering

---

## Overzicht

| # | Issue | Prioriteit | Status |
|---|-------|------------|--------|
| 1 | TTS klinkt soms Engelserig | Hoog | ✅ Opgelost |
| 2 | Text normalisatie (nieuw!) | Hoog | ✅ Geïmplementeerd |
| 3 | Temperature/top_p tuning | Hoog | ✅ Getest (0.4/0.55) |
| 4 | Langere reference audio | Medium | Optioneel |
| 5 | Prosody/expressie markers | Laag | Optioneel |
| 6 | Snellere audio response | Laag | Pseudo-streaming |
| 7 | Playback interrupt | Laag | Spatiebalk |

**Verwijderd uit plan (niet meer van toepassing):**
- ~~VRAM memory leak~~ - Geen issue bij Fish Audio
- ~~Voxtral NL taal~~ - Al gedaan (`language: 'nl'` in vad_conversation.py:110)
- ~~Context sliding window~~ - Geen actueel probleem
- ~~Noise removal~~ - ElevenLabs audio is al clean
- ~~Korte zinnen~~ - Opgelost via system prompt (2026-01-16)

---

## 1. TTS Klinkt Soms Engelserig

### Status: ✅ Deels opgelost (2026-01-16)

**Uitgevoerd:**
- System prompt aangepast met "Gebruik bij voorkeur Nederlandse woorden"
- Korte antwoorden (1-3 zinnen) in plaats van lange teksten
- Geen markdown formatting (geen **, -, of genummerde lijsten)
- Robot capabilities en beperkingen toegevoegd aan prompt

**Nog te doen:**
- Text normalisatie (punt 2) voor acroniemen en getallen
- Optioneel: temperature/top_p tuning (punt 3)

### Oorspronkelijk probleem
Via orchestrator klonk TTS soms met Engels accent door:
- LLM die Engelse woorden/zinstructuren gebruikte
- Markdown formatting die TTS niet kon uitspreken
- Te lange antwoorden met opsommingen

---

## 2. Text Normalisatie

### Status: ✅ Geïmplementeerd (2026-01-16)

**Wat het doet:**
- Acroniemen → Nederlandse fonetiek: "API" → "aa-pee-ie", "ASML" → "aa-es-em-el"
- Getallen → woorden: "247" → "tweehonderdzevenenveertig"
- Haakjes → eerste `(` wordt komma, rest verwijderd (Fish Audio slaat haakjes over)
- Specifieke woorden: "Docker" → "dokker"

**Bestanden:**
- `orchestrator/main.py` - `normalize_for_tts()` functie
- `vad_conversation.py` - toont genormaliseerde tekst als `📝 [TTS]`

**Dependencies:**
```bash
pip install num2words  # in nerdcarx-vad conda env
```

---

## 3. Temperature/Top_p Tuning

### Status: ✅ Getest (2026-01-16)

**Gekozen waarden:**
```yaml
temperature: 0.4
top_p: 0.55
```

**Bevindingen:**
- temp=0.2, top_p=0.5 → te saai
- temp=0.3, top_p=0.6 → meer leven, maar uitspraak slechter (letters ingeslikt)
- temp=0.4, top_p=0.55 → beste compromis

**Bekende beperkingen:**
- Intonatie nog wat vlak/saai
- Sommige woorden Engels uitgesproken ("Nederlands" → "Netherlands", "machines" → "masjiens")
- Fine-tunen met betere reference audio (punt 4)

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
| Lengte | ✅ ~10s | Fish Audio adviseert 10-30s |
| Variatie | ⚠️ Beperkt | Geen vraagzin, cijfers, afkortingen |
| Kwaliteit | ✅ Goed | ElevenLabs bron |

### Optioneel: "NL Torture Test" Reference

Als NL uitspraak niet goed genoeg is, maak een uitgebreide reference (20-25 seconden) die alle lastige Nederlandse klanken bevat:

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
| Allersnelste mogelijke response | WebSocket streaming is voor Fish Audio CLOUD API/SDK |
| Professionele UX | Lokale fish-speech HTTP server ondersteunt dit NIET |
| | HTTP `stream=true` geeft vaak ruis/klikken |
| | Complexe implementatie |

**Waarom dit NIET voor ons werkt:**

1. **WebSocket streaming = Fish Audio cloud API/SDK**
   - De officiële real-time WebSocket streaming docs (`stream_websocket`, `convertRealtime`) horen bij de **Fish Audio cloud API en SDK**
   - Dit is NIET beschikbaar in de lokale `fish-speech` Docker/HTTP server die wij draaien

2. **Lokale fish-speech server = alleen HTTP**
   - Onze setup: lokale Docker container met HTTP `/v1/tts` endpoint
   - `stream=true` via HTTP geeft ruis omdat chunks "netwerk pakketjes" zijn, geen nette audio blokken

3. **Conclusie**
   - Voor cloud: WebSocket streaming mogelijk via Fish Audio SDK
   - Voor lokaal (wij): Pseudo-streaming per zin is de juiste aanpak

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
import re

def split_into_sentences(text: str) -> list[str]:
    """
    Split tekst in zinnen, maar bescherm afkortingen.

    Let op: Simpele regex splitst ook op "Dr.", "bv.", "etc."
    Daarom eerst afkortingen tijdelijk vervangen.
    """

    # 1. Bescherm bekende afkortingen (vervang punt tijdelijk)
    # NOTE: Gebruik regex voor case-insensitive matching indien nodig
    protected = [
        (r'\bDr\.', 'Dr<DOT>'),
        (r'\bMr\.', 'Mr<DOT>'),
        (r'\bbv\.', 'bv<DOT>'),
        (r'\bbijv\.', 'bijv<DOT>'),
        (r'\betc\.', 'etc<DOT>'),
        (r'\bevt\.', 'evt<DOT>'),
        (r'\bincl\.', 'incl<DOT>'),
        (r'\bexcl\.', 'excl<DOT>'),
        (r'\bnr\.', 'nr<DOT>'),
        (r'\bca\.', 'ca<DOT>'),
        (r'\bo\.a\.', 'o<DOT>a<DOT>'),
        (r'\bi\.p\.v\.', 'i<DOT>p<DOT>v<DOT>'),
    ]

    for pattern, placeholder in protected:
        text = re.sub(pattern, placeholder, text, flags=re.IGNORECASE)

    # 2. Split op zin-einden (. ! ? gevolgd door spatie of einde)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # 3. Herstel afkortingen
    restore = [
        ('Dr<DOT>', 'Dr.'), ('Mr<DOT>', 'Mr.'), ('bv<DOT>', 'bv.'),
        ('bijv<DOT>', 'bijv.'), ('etc<DOT>', 'etc.'), ('evt<DOT>', 'evt.'),
        ('incl<DOT>', 'incl.'), ('excl<DOT>', 'excl.'), ('nr<DOT>', 'nr.'),
        ('ca<DOT>', 'ca.'), ('o<DOT>a<DOT>', 'o.a.'), ('i<DOT>p<DOT>v<DOT>', 'i.p.v.'),
    ]
    result = []
    for s in sentences:
        for placeholder, abbr in restore:
            s = s.replace(placeholder, abbr)
        if s.strip():
            result.append(s.strip())

    return result

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
Buffer kort (150-300ms) voordat je begint af te spelen → voorkomt "gaten" door netwerk-jitter.

> **Note:** Dit past bij Fish Audio's advies: "Buffer 2-3 audio chunks" voor smooth playback.
> Cross-fading tussen chunks is optioneel - bij pseudo-streaming per zin is buffering meestal genoeg.

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

### Belangrijk: TTS parallel, afspelen in-order

Bij geavanceerde implementatie: start TTS-tasks **parallel** (async queue), maar speel audio altijd **in volgorde** af. Anders krijg je zinnen door elkaar!

> **Let op:** Limiteer concurrency tot max 2-3 zinnen tegelijk, anders kun je je GPU onnodig laten thrashen. Dit is voor fase 2/3.

```python
import asyncio

async def parallel_tts_ordered_playback(sentences, client, max_concurrent=2):
    """TTS parallel starten (gelimiteerd), maar in volgorde afspelen."""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_tts(sentence):
        async with semaphore:
            return await synthesize_speech(sentence, emotion, client)

    # Start alle TTS tasks (maar max 2-3 tegelijk actief)
    tasks = [
        asyncio.create_task(limited_tts(s))
        for s in sentences
    ]

    # Wacht en speel af in originele volgorde
    for task in tasks:
        audio = await task
        yield audio  # Altijd in volgorde
```

### Wanneer implementeren?

| Versie | Complexiteit | Wanneer |
|--------|--------------|---------|
| Basis (per zin, sequentieel) | Laag | Als huidige latency stoort |
| + Pipelining | Medium | Voor langere antwoorden |
| + Parallel TTS | Medium | Voor maximale snelheid |
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
