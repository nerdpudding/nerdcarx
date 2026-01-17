# Remote Tool Pattern

**Beslissing:** [D016](../../DECISIONS.md#d016-remote-tool-pattern---tools-op-pi-vs-desktop)
**Gebruikt in:** NerdCarX Fase 3+

---

## Wat is het probleem?

NerdCarX heeft twee computers die samenwerken:
- **Desktop** - doet het "denken" (spraakherkenning, AI, spraaksynthese)
- **Raspberry Pi** - doet het "doen" (camera, scherm, motoren)

De AI (LLM) kan "tools" aanroepen. Bijvoorbeeld:
- "Maak een foto" → `take_photo`
- "Toon een blije emotie" → `show_emotion`
- "Zoek op internet" → `web_search`

**Het probleem:** Sommige tools moeten op de Desktop draaien, andere op de Pi.

| Tool | Waar | Waarom |
|------|------|--------|
| `take_photo` | Pi | Camera zit op de Pi |
| `show_emotion` | Pi | OLED scherm zit op de Pi |
| `web_search` | Desktop | Internet toegang via Desktop |

Hoe weet de software welke tools waar moeten draaien?

---

## De oplossing: `is_remote` property

Elke tool "weet" zelf waar hij hoort door middel van een `is_remote` eigenschap:

```python
class TakePhotoTool:
    @property
    def is_remote(self) -> bool:
        return True  # Ik moet op de Pi draaien

class WebSearchTool:
    @property
    def is_remote(self) -> bool:
        return False  # Ik draai op de Desktop
```

De handler (de code die tools uitvoert) checkt deze eigenschap:

```python
if tool.is_remote:
    # Stuur naar Pi en wacht op resultaat
else:
    # Voer hier lokaal uit
```

---

## Waarom deze aanpak?

### Alternatief 1: Centrale lijst

Je zou een lijst kunnen bijhouden van alle remote tools:

```python
# Ergens in de code
REMOTE_TOOLS = ["take_photo", "show_emotion", "drive"]
```

**Probleem:** Als je een nieuwe tool toevoegt, moet je op twee plekken code aanpassen:
1. De tool class maken
2. De lijst updaten

Als je stap 2 vergeet → bug. De informatie "waar draait deze tool" staat los van de tool zelf.

### Alternatief 2: Aparte registries

Je zou twee aparte lijsten kunnen hebben:

```python
pi_tools = PiToolRegistry()       # Tools voor de Pi
desktop_tools = DesktopToolRegistry()  # Tools voor Desktop
```

**Probleem:** Je moet nog steeds onthouden om de tool in de juiste registry te registreren. Zelfde probleem als de centrale lijst.

### Waarom `is_remote` beter is

Met de `is_remote` property:
- **Eén plek:** Alle informatie over de tool staat bij de tool zelf
- **Niet te vergeten:** Als je een tool maakt, zet je `is_remote` erbij
- **Logisch:** "Waar draai ik" is een eigenschap van de tool, net als "wat is mijn naam"

---

## SOLID principes

Dit pattern volgt twee belangrijke SOLID principes:

### Single Responsibility Principle (SRP)

> "Een class moet één reden hebben om te veranderen"

De tool class is verantwoordelijk voor alles over die tool:
- Naam
- Beschrijving
- Parameters
- **Waar hij draait** (`is_remote`)

Je hoeft niet ergens anders te kijken om te weten waar de tool hoort.

### Open/Closed Principle (OCP)

> "Open voor uitbreiding, gesloten voor modificatie"

Als je een nieuwe tool toevoegt:
- **Open voor uitbreiding:** Je maakt een nieuwe class met `is_remote`
- **Gesloten voor modificatie:** De handler code hoeft niet te veranderen

Voorbeeld - nieuwe tool toevoegen:

```python
# Nieuwe tool - alleen dit bestand aanmaken
class DriveTool:
    @property
    def name(self) -> str:
        return "drive"

    @property
    def is_remote(self) -> bool:
        return True  # Motoren zitten op Pi

    async def execute(self, arguments: dict) -> str:
        # Implementatie
        ...
```

De handler werkt automatisch met deze nieuwe tool - geen wijzigingen nodig.

---

## Hoe werkt het in de praktijk?

### Stap 1: LLM roept tool aan

De gebruiker zegt "wat zie je?" en de LLM besluit `take_photo` aan te roepen.

### Stap 2: Handler checkt is_remote

```python
tool = registry.get("take_photo")
if tool.is_remote:
    # Ga naar stap 3
else:
    # Voer lokaal uit
```

### Stap 3: Stuur naar Pi

De handler stuurt een `FUNCTION_REQUEST` message naar de Pi:

```json
{
  "type": "function_request",
  "payload": {
    "name": "take_photo",
    "arguments": {"question": "wat zie je?"},
    "request_id": "abc123"
  }
}
```

### Stap 4: Pi voert uit

De Pi ontvangt het verzoek, maakt een foto, en stuurt het resultaat terug:

```json
{
  "type": "function_result",
  "payload": {
    "request_id": "abc123",
    "name": "take_photo",
    "result": "foto gemaakt",
    "image_base64": "..."
  }
}
```

### Stap 5: Handler gaat verder

De handler ontvangt de foto en geeft deze aan de LLM voor analyse.

---

## Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DESKTOP                                  │
│                                                                  │
│  ┌──────────┐    ┌─────────────┐    ┌──────────────────────┐   │
│  │   LLM    │───►│   Handler   │───►│ tool.is_remote?      │   │
│  └──────────┘    └─────────────┘    └──────────┬───────────┘   │
│       │                                        │                │
│       │                           ┌────────────┴────────────┐   │
│       │                           │                         │   │
│       │                      is_remote=False           is_remote=True
│       │                           │                         │   │
│       │                           ▼                         │   │
│       │                    ┌──────────────┐                 │   │
│       │                    │ Voer lokaal  │                 │   │
│       │                    │ uit (Desktop)│                 │   │
│       │                    └──────────────┘                 │   │
│       │                                                     │   │
└───────┼─────────────────────────────────────────────────────┼───┘
        │                                                     │
        │                    WebSocket                        │
        │                                                     ▼
┌───────┼─────────────────────────────────────────────────────────┐
│       │                         PI                               │
│       │                                                          │
│       │              ┌───────────────────────┐                   │
│       │              │ FUNCTION_REQUEST      │                   │
│       │              │ ontvangen             │                   │
│       │              └───────────┬───────────┘                   │
│       │                          │                               │
│       │                          ▼                               │
│       │              ┌───────────────────────┐                   │
│       │              │ Tool uitvoeren        │                   │
│       │              │ (camera, OLED, etc.)  │                   │
│       │              └───────────┬───────────┘                   │
│       │                          │                               │
│       │                          ▼                               │
│       │              ┌───────────────────────┐                   │
│       │              │ FUNCTION_RESULT       │                   │
│       ◄──────────────│ terugsturen           │                   │
│                      └───────────────────────┘                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Wanneer gebruik je dit pattern?

Dit pattern is handig wanneer:

1. **Je hebt meerdere executielocaties** (Desktop, Pi, cloud, etc.)
2. **Tools weten inherent waar ze horen** (camera = Pi, internet = Desktop)
3. **Je wilt makkelijk nieuwe tools toevoegen** zonder bestaande code te wijzigen

Dit pattern is NIET nodig wanneer:

1. Alle tools op dezelfde plek draaien
2. De executielocatie configureerbaar moet zijn (dan is config.yml beter)

---

## Samenvatting

| Aspect | Uitleg |
|--------|--------|
| **Wat** | Elke tool heeft een `is_remote` property |
| **Waarom** | Tool weet zelf waar hij hoort (Single Responsibility) |
| **Voordeel** | Nieuwe tools toevoegen zonder handler te wijzigen (Open/Closed) |
| **Alternatief** | Centrale lijst of aparte registries - makkelijk vergeten te updaten |

---

## Referenties

- [D016 in DECISIONS.md](../../DECISIONS.md#d016-remote-tool-pattern---tools-op-pi-vs-desktop)
- [ARCHITECTURE.md - Function Calling sectie](../../ARCHITECTURE.md)
- [Fase 3 Implementation Plan](../../fase3-pi/Fase3_Implementation_Plan.md)
- [SOLID Principles (Wikipedia)](https://en.wikipedia.org/wiki/SOLID)
