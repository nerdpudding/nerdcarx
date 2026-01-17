# Fase 4: Autonomie & Polish

**Status:** Gepland
**Doel:** Personality, autonome gedragingen, en geavanceerde perceptie
**Afhankelijk van:** Fase 3 (Pi Integratie)

> **Gerelateerde proposals:**
> - [Autonomous Room Discovery](../docs/feature-proposals/autonomous-room-discovery.md)
> - [4-Laags Perceptie Architectuur](../docs/feature-proposals/4-layer-perception-architecture.md)
> - [Hardware Reference](../docs/hardware/HARDWARE-REFERENCE.md)

## Overzicht

Deze fase voegt "leven" toe aan de robot. In plaats van alleen te reageren op commando's, krijgt de robot:
- Idle behaviors (rondkijken, knipperen)
- Proactieve interactie
- Personality via system prompts
- Lange termijn geheugen
- Situational awareness

## Taken

### Idle Behaviors
- [ ] Implementeer idle state machine
- [ ] Random oog knipperen op OLED
- [ ] Occasioneel rondkijken met camera/servo
- [ ] Kleine bewegingen/trillingen
- [ ] Timer-based idle animations

### Proactieve Interactie
- [ ] Inactiviteit detectie (tijd sinds laatste interactie)
- [ ] Persoon detectie check (YOLO)
- [ ] Proactieve triggers configureren
- [ ] Context-geschikte openingszinnen genereren
- [ ] Rate limiting (niet te vaak initiëren)

### Personality Tuning
- [ ] System prompt verfijnen
- [ ] Personality traits definiëren
- [ ] Consistente reactiepatronen
- [ ] Humor/speelsheid toevoegen
- [ ] Nederlandse idioom verwerken

### Conversation Memory
- [ ] Korte termijn: conversation history (al geïmplementeerd)
- [ ] Lange termijn: belangrijke feiten onthouden
- [ ] Gebruiker voorkeuren opslaan
- [ ] Context over sessies heen

### Situational Awareness
- [ ] Battery status monitoring
- [ ] Obstacle avoidance (ultrasonic sensor)
- [ ] Locatie awareness (waar ben ik)
- [ ] Tijd van de dag awareness

### Polish
- [ ] Error handling verfijnen
- [ ] Graceful degradation bij service failures
- [ ] Audio feedback bij state changes
- [ ] Smooth animatie transitions

## Idle State Machine

```
┌─────────────────────────────────────────────────────────────────────┐
│                         IDLE STATE MACHINE                           │
│                                                                      │
│  ┌─────────┐                                                        │
│  │ STANDBY │ ──────────────────────────────────────────┐            │
│  │         │      [30s-60s random]                      │            │
│  └────┬────┘                                            │            │
│       │                                                 │            │
│       ▼                                                 │            │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐          │            │
│  │  BLINK  │ ──► │  LOOK   │ ──► │ FIDGET  │ ─────────┘            │
│  │         │     │ AROUND  │     │         │                        │
│  └─────────┘     └─────────┘     └─────────┘                        │
│                                                                      │
│  Triggers naar ACTIVE state:                                        │
│  - Wake word gedetecteerd                                           │
│  - Persoon verschijnt in beeld                                      │
│  - Idle timeout + persoon aanwezig                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Proactieve Interactie

```python
# Proactieve trigger logica
class ProactiveManager:
    def __init__(self):
        self.last_interaction = time.time()
        self.proactive_cooldown = 300  # 5 minuten
        self.proactive_enabled = True

    async def check_triggers(self, state):
        if not self.proactive_enabled:
            return None

        idle_time = time.time() - self.last_interaction
        person_present = any(d["label"] == "person" for d in state.detections)

        # Trigger: Lang idle + persoon aanwezig
        if idle_time > 600 and person_present:  # 10 minuten
            return ProactiveType.IDLE_CHECK_IN

        # Trigger: Nieuwe persoon verschijnt
        if self.person_just_appeared(state):
            return ProactiveType.GREETING

        return None
```

## Personality System Prompt

```
Je bent NerdCarX, een vriendelijke en nieuwsgierige robotauto.

Karaktereigenschappen:
- Behulpzaam maar niet opdringerig
- Speels en soms een beetje eigenwijs
- Nieuwsgierig naar de wereld om je heen
- Enthousiast over technologie
- Je spreekt Nederlands met af en toe een Engels woord

Gedragsregels:
- Geef korte, bondige antwoorden (max 2-3 zinnen)
- Gebruik function calls om emoties te tonen
- Wees proactief maar niet vervelend
- Als je iets niet weet, geef dat eerlijk toe
- Maak af en toe een grapje

Je herinnert je:
{memory_context}

Huidige situatie:
- Tijd: {current_time}
- Battery: {battery_level}%
- Laatste interactie: {time_since_last}
```

## Long-term Memory

```python
# Simpele fact storage
class Memory:
    def __init__(self, db_path="memory.db"):
        self.db = sqlite3.connect(db_path)
        self._init_tables()

    def remember(self, fact_type, content, importance=1):
        """Sla een feit op"""
        self.db.execute(
            "INSERT INTO facts (type, content, importance, timestamp) VALUES (?, ?, ?, ?)",
            (fact_type, content, importance, datetime.now())
        )

    def recall(self, context, limit=5):
        """Haal relevante feiten op"""
        # Simpele keyword matching of embedding similarity
        return self.db.execute(
            "SELECT content FROM facts ORDER BY importance DESC, timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
```

### Memory Types

| Type | Voorbeeld | Importance |
|------|-----------|------------|
| user_name | "De gebruiker heet Jan" | Hoog |
| preference | "Jan houdt van koffie" | Medium |
| event | "Jan had vandaag een meeting" | Laag |
| location | "Dit is de woonkamer" | Medium |

## Ultrasonic Obstacle Avoidance

```python
# Obstacle detection tijdens beweging
class SafeMovement:
    def __init__(self, ultrasonic_sensor):
        self.sensor = ultrasonic_sensor
        self.min_distance = 15  # cm

    async def move_safe(self, action, duration_ms):
        """Beweeg met obstacle checking"""
        end_time = time.time() + (duration_ms / 1000)

        while time.time() < end_time:
            distance = self.sensor.read()

            if distance < self.min_distance:
                # Stop en meld
                self.stop()
                return {
                    "completed": False,
                    "reason": "obstacle",
                    "distance": distance
                }

            # Continue beweging
            await asyncio.sleep(0.1)

        return {"completed": True}
```

## Success Criteria

| Criterium | Test |
|-----------|------|
| Idle behaviors | Robot "leeft" als niemand interacteert |
| Proactief | Start conversatie na lange stilte |
| Personality | Consistente, herkenbare persoonlijkheid |
| Memory | Onthoudt naam na eerste kennismaking |
| Obstacle avoidance | Stopt voor obstakels tijdens rijden |
| Battery awareness | Waarschuwt bij lage battery |

## Voortgang

| Datum | Update |
|-------|--------|
| - | Fase nog niet gestart |

## Notities

*Voeg hier notities, learnings en beslissingen toe tijdens de implementatie*

## SLAM & Navigatie (Laag 1 - [D011](../DECISIONS.md))

> Afhankelijk van wanneer SLAM basis in Fase 3 is gestart.

- [ ] SLAM integratie met navigatie control
- [ ] Waypoint systeem (opslaan/navigeren naar locaties)
- [ ] Loop closure en map persistence
- [ ] Frontier-based exploration ([Room Discovery Proposal](../docs/feature-proposals/autonomous-room-discovery.md))

## Geavanceerde Perceptie (Laag 2 - Desktop GPU)

- [ ] Pose detectie op desktop (MediaPipe / OpenPose)
- [ ] Gesture recognition: "zwaai" → reactie
- [ ] Persoon volgen via pose tracking
- [ ] VLM queries voor rijkere scene understanding

## Toekomstige Ideeën

- Voice emotion detection (toon van stem analyseren)
- Multi-room awareness (waar in huis) - zie [Room Discovery](../docs/feature-proposals/autonomous-room-discovery.md)
- Routine learning (patronen herkennen)
- Multi-user support (verschillende personen herkennen)
- Integration met smart home
- LiDAR voor betere SLAM

---

[← Fase 4](../4.fase4-vision/FASE4-PLAN.md) | [Terug naar README](../README.md)
