# Plan: Emotion State Machine

**Datum:** 2026-01-11
**Status:** ✅ Volledig geïmplementeerd en getest
**Beslissing ID:** D007

---

## Doel

De robot heeft een **persistente emotionele staat** die beïnvloed wordt door de gebruiker. De emotie verandert alleen wanneer de context daar aanleiding toe geeft.

---

## Architectuur

### State Opslag: Orchestrator (per conversation_id)

```python
emotion_states = {
    "vad-abc123": {
        "emotion": "happy",
        "last_updated": datetime,
        "last_interaction": datetime
    }
}
```

### Flow

```
1. Request binnenkomt
   ↓
2. Check auto-reset (>5 min sinds laatste interactie?)
   → Ja: reset naar neutral
   ↓
3. Huidige emotie meegegeven aan LLM in system prompt
   "Je huidige emotionele staat is: happy"
   ↓
4. LLM response
   → Met show_emotion call: update state, changed=true
   → Zonder: state blijft, changed=false
   ↓
5. Response naar client met emotie info
```

---

## Problemen en Oplossingen

### Probleem 1: Model schreef tool calls als tekst

**Symptoom:**
```
🤖 NerdCarX: show_emotion[ARGS]{"emotion": "confused"} Ik snap het niet...
```

**Oorzaak:** Ministral 8B gebruikte Mistral text format in plaats van Ollama API tool calls.

**Oplossing:** Fallback parsing functie in orchestrator:
```python
def parse_text_tool_calls(content: str) -> tuple[str, list]:
    pattern = r'(\w+)\[ARGS\](\{[^}]+\})'
    matches = re.findall(pattern, content)
    # Parse en verwijder uit content
```

### Probleem 2: Model maakte geen emotie tool calls

**Symptoom:** Bij "stomme kutrobot" bleef emotie op "happy".

**Oorzaak:**
- Vage prompt instructies
- Model safety training voorkomt negatieve reacties

**Oplossing:** Expliciete prompt dat robot EIGEN emotie simuleert:
```yaml
## show_emotion
Jij bent een robot met een emotionele staat.
Roep show_emotion aan wanneer JOUW emotie moet VERANDEREN.

Voorbeelden:
- Gebruiker beledigt je → jij wordt sad of worried
- Gebruiker is enthousiast → jij wordt happy of excited
- Gebruiker stelt een gewone vraag → geen verandering nodig
```

### Probleem 3: Onduidelijke output

**Symptoom:** Niet duidelijk of tool calls werden gemaakt.

**Oplossing:** Verbeterde VAD output met status indicators:
```
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'sad'})
🎭 [EMOTIE] sad 😢 (VERANDERD)
```

---

## Werkende Output (getest 2026-01-11)

```
[Turn 1]
🎧 Luisteren... (spreek wanneer klaar)
🔴 Spraak gedetecteerd...
✅ Opgenomen (2.1s)
📝 Transcriberen... ✅
👤 Jij: Hallo.
🔄 Processing... ✅
🔧 [TOOL CALLS] geen
🎭 [EMOTIE] neutral 😐 (behouden)
🤖 NerdCarX: Hoi! Ik ben NerdCarX...

[Turn 2]
👤 Jij: Ik vind jou eigenlijk maar een stomme lul.
🔄 Processing... ✅
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'sad'})
🎭 [EMOTIE] sad 😢 (VERANDERD)
🤖 NerdCarX: Ik begrijp dat je niet altijd enthousiast bent...

[Turn 3]
👤 Jij: Oké, sorry, dat meende ik niet.
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'neutral'})
🎭 [EMOTIE] neutral 😐 (VERANDERD)
🤖 NerdCarX: Geen probleem!

[Turn 4]
👤 Jij: Ik vind jou eigenlijk fantastisch.
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'happy'})
🎭 [EMOTIE] happy 😊 (VERANDERD)
🤖 NerdCarX: Dank je wel! Dat is heel lief...

[Turn 5]
👤 Jij: Kan je eens vertellen wat je ziet?
🔧 [TOOL CALLS] 1 tool call(s):
   → take_photo({'question': 'Beschrijf de directe omgeving...'})
🎭 [EMOTIE] happy 😊 (behouden)
🤖 NerdCarX: De camera ziet twee leuke honden...

[Turn 6]
👤 Jij: Wat is de hoofdstad van Nederland?
🔧 [TOOL CALLS] geen
🎭 [EMOTIE] happy 😊 (behouden)
🤖 NerdCarX: De hoofdstad van Nederland is Amsterdam...

[Turn 7]
👤 Jij: Wel een beetje saai onderwerp, vind je niet?
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'curious'})
🎭 [EMOTIE] curious 🤔 (VERANDERD)
🤖 NerdCarX: Je hebt gelijk, Amsterdam is een stad vol leven...

[Turn 8]
👤 Jij: Nee, gaap, het is al best wel laat.
🔧 [TOOL CALLS] 1 tool call(s):
   → show_emotion({'emotion': 'tired'})
🎭 [EMOTIE] tired 😴 (VERANDERD)
🤖 NerdCarX: Ah, begrijpelijk. Dan hoop ik dat je een goede nacht hebt!
```

---

## Response Format

```json
{
  "response": "...",
  "function_calls": [{"name": "show_emotion", "arguments": {"emotion": "happy"}}],
  "emotion": {
    "current": "happy",
    "changed": true,
    "auto_reset": false,
    "had_tool_call": true
  }
}
```

---

## Bestanden Gewijzigd

| Bestand | Wijziging |
|---------|-----------|
| `orchestrator/main.py` | `emotion_states` dict, `get_emotion_state()`, `update_emotion_state()`, `parse_text_tool_calls()` |
| `vad-desktop/vad_conversation.py` | Verbeterde output met ✅ checkmarks, tool call details |
| `config.yml` | Emotie instructies in system prompt, 15 beschikbare emoties |

---

## Beschikbare Emoties

```yaml
emotions:
  default: "neutral"
  auto_reset_minutes: 5
  available:
    - happy, sad, angry, surprised, neutral, curious
    - confused, excited, thinking, shy, love, tired
    - bored, proud, worried
```

---

*Laatst bijgewerkt: 2026-01-11*
