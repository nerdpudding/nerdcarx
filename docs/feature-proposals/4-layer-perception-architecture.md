# Feature Proposal: 4-Laags Perceptie Architectuur

## Samenvatting

Een modulaire perceptie architectuur die verantwoordelijkheden scheidt naar waar ze thuishoren: safety-critical lokaal op de Pi, zware AI op de desktop GPU. Dit maakt het systeem robuust, schaalbaar en SOLID-compliant.

---

## Waarom Deze Architectuur?

### Het Probleem

Een robot heeft verschillende soorten perceptie nodig met verschillende eisen:

| Taak | Latency Eis | Betrouwbaarheid | Compute |
|------|-------------|-----------------|---------|
| Obstacle avoidance | <50ms | Moet ALTIJD werken | Licht |
| SLAM/navigatie | Real-time | Mag niet haperen | Medium |
| Pose detectie | ~200ms ok | Nice-to-have | Zwaar |
| Conversatie (STT/LLM/TTS) | Niet kritisch | Kan even wachten | Zeer zwaar |

**Probleem:** Als alles op de desktop draait en WiFi hapert, botst de robot.

### De Oplossing: Scheiding van Verantwoordelijkheden

```
┌─────────────────────────────────────────────────────────────────────┐
│                    4-LAAGS PERCEPTIE ARCHITECTUUR                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LAAG 0: SAFETY          ──────────────────────────►  Pi lokaal     │
│  Obstacle avoidance, noodstop                         <50ms         │
│  ✓ Werkt zonder WiFi                                                │
│                                                                      │
│  LAAG 1: NAVIGATIE       ──────────────────────────►  Pi lokaal     │
│  SLAM, route planning, localisatie                    Real-time     │
│  ✓ Stabiele control loops                                           │
│                                                                      │
│  LAAG 2: PERCEPTIE       ──────────────────────────►  Desktop GPU   │
│  Pose detectie, VLM, heavy detection                  ~200ms ok     │
│  ✓ Flexibiliteit voor zware modellen                                │
│                                                                      │
│  LAAG 3: CONVERSATIE     ──────────────────────────►  Desktop GPU   │
│  STT → LLM → TTS                                      Niet kritisch │
│  ✓ Al geimplementeerd in Fase 1                                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Hoe Past Dit in de SOLID/Modulaire Aanpak?

### Single Responsibility

Elke laag heeft één verantwoordelijkheid:
- Laag 0: Robot veilig houden
- Laag 1: Weten waar de robot is
- Laag 2: Begrijpen wat de robot ziet
- Laag 3: Communiceren met de gebruiker

### Loose Coupling (Fase 2)

Lagen communiceren via gedefinieerde interfaces:

```
┌──────────────┐     HTTP/WS      ┌──────────────┐
│   Pi Client  │ ◄──────────────► │  Orchestrator│
│              │                  │   (Desktop)  │
│  Laag 0 + 1  │                  │  Laag 2 + 3  │
└──────────────┘                  └──────────────┘
```

- Pi stuurt: audio, video frames, sensor data
- Desktop stuurt: TTS audio, function calls, perceptie events
- Protocol: JSON over WebSocket (zie `fase3-pi/PLAN.md`)

### Dependency Injection (Fase 2)

Services zijn inwisselbaar:
```python
# config.yml bepaalt welke implementatie
perception:
  layer0_safety: "yolo_nano"      # of "ultrasonic_only"
  layer1_slam: "orb_slam3"        # of "rtab_map" of "disabled"
  layer2_pose: "mediapipe"        # of "openpose"
```

---

## Use Cases per Laag

### Laag 0: Safety (Fase 3)

| Use Case | Trigger | Actie |
|----------|---------|-------|
| Obstakel voor | YOLO/ToF detectie <30cm | Motor stop |
| Obstakel links/rechts | ToF sensor <20cm | LED waarschuwing |
| Geen WiFi | Connection lost | Blijf stil staan |

**Hardware:** Camera Module 3 + YOLO nano + ToF sensors + Ultrasonic
**Zie:** [HARDWARE-REFERENCE.md](../hardware/HARDWARE-REFERENCE.md)

### Laag 1: Navigatie (Fase 3/4)

| Use Case | Trigger | Actie |
|----------|---------|-------|
| "Rij naar de keuken" | LLM tool call | SLAM waypoint navigatie |
| Exploratie | "Verken het huis" | Frontier-based exploration |
| Localisatie | "Waar ben je?" | Positie in map opzoeken |

**Zie:** [autonomous-room-discovery.md](autonomous-room-discovery.md)

### Laag 2: Perceptie (Fase 4)

| Use Case | Trigger | Actie |
|----------|---------|-------|
| Zwaai-reactie | Pose: hand omhoog | Emotie "excited", begroeting |
| Persoon volgen | Pose tracking | Camera pan/tilt aanpassen |
| Scene beschrijving | "Wat zie je?" | VLM query op desktop |

### Laag 3: Conversatie (Fase 1 - al klaar)

| Use Case | Trigger | Actie |
|----------|---------|-------|
| Vraag beantwoorden | Spraak input | STT → LLM → TTS |
| Emotie tonen | LLM tool call | OLED update |
| Foto analyseren | "Wat zie je?" | Vision + LLM |

---

## Camera Module 3: Dual Vision Pad

De Camera Module 3 (IMX708) voedt beide paden:

```
                     Camera Module 3 (IMX708)
                              │
                              │ picamera2 frame capture
                              ▼
                    ┌─────────────────────┐
                    │   Frame Distributor │
                    │   (lokaal op Pi)    │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┴───────────────────┐
           │                                       │
           ▼                                       ▼
    ┌──────────────┐                      ┌──────────────┐
    │   Lokaal     │                      │   Desktop    │
    │              │                      │              │
    │ • YOLO nano  │                      │ • Pose model │
    │ • SLAM feed  │                      │ • VLM        │
    │              │                      │              │
    └──────┬───────┘                      └──────┬───────┘
           │                                     │
           │ Laag 0+1                            │ Laag 2
           │ <50ms                               │ ~200ms
           ▼                                     ▼
    ┌──────────────┐                      ┌──────────────┐
    │ Motor ctrl   │                      │ Events naar  │
    │ LED ctrl     │                      │ orchestrator │
    └──────────────┘                      └──────────────┘
```

### Waarom Camera Module 3?

| Aspect | Keuze | Reden |
|--------|-------|-------|
| Camera | CM3 (IMX708) ipv AI Camera (IMX500) | Flexibiliteit: elk model, lokaal + remote |
| Features | Autofocus, HDR | Variabele lichtomstandigheden |
| Prijs | ~€25 | Desktop GPU doet het zware werk |

**Beslissing:** [D010 in DECISIONS.md](../../DECISIONS.md)

---

## Bijdrage aan Einddoel (Fase 4)

Deze architectuur maakt de Fase 4 features mogelijk:

| Fase 4 Feature | Afhankelijk van Laag |
|----------------|---------------------|
| Idle behaviors (knipperen, rondkijken) | Laag 0 (camera) |
| Proactieve interactie (persoon detectie) | Laag 2 (pose) |
| "Rij naar de keuken" | Laag 1 (SLAM) |
| "Wat zie je?" met rijke beschrijving | Laag 2 (VLM) |
| Obstacle avoidance tijdens rijden | Laag 0 (safety) |
| Gesture recognition (zwaai-reactie) | Laag 2 (pose) |

---

## Implementatie Roadmap

| Fase | Wat | Laag |
|------|-----|------|
| 1 | STT + LLM + TTS + Vision (take_photo) | 3 |
| 2 | Refactor, dockerizen, API's stabiel | - |
| 3 | Camera Module 3, YOLO safety, ToF, (opt. SLAM basis) | 0, (1) |
| 4 | SLAM compleet, Pose detectie, Room discovery | 1, 2 |

---

## Gerelateerde Documenten

- [HARDWARE-REFERENCE.md](../hardware/HARDWARE-REFERENCE.md) - Definitieve hardware configuratie
- [autonomous-room-discovery.md](autonomous-room-discovery.md) - Laag 1 feature proposal
- [fase3-pi/PLAN.md](../../fase3-pi/PLAN.md) - Pi integratie taken
- [fase4-autonomie/PLAN.md](../../fase4-autonomie/PLAN.md) - Autonomie features
- [DECISIONS.md](../../DECISIONS.md) - D010 (Camera), D011 (4-laags), D012 (Hardware)
