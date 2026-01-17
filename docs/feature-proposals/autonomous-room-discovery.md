# Feature Proposal: Autonomous Room Discovery

## Samenvatting

NerdCarX kan zelfstandig een omgeving verkennen, een kaart bouwen, en kamers labelen. Dit maakt natuurlijke navigatie commando's mogelijk zoals "rij naar de keuken".

**Architectuur laag:** Laag 1 (Navigatie) - zie [4-layer-perception-architecture.md](4-layer-perception-architecture.md)
**Fase:** 4 (Autonomie)
**Afhankelijk van:** Fase 3 (Pi Integratie met Camera Module 3)

---

## Motivatie

**Huidige situatie:** Robot kan obstakels reactief ontwijken maar heeft geen ruimtelijk geheugen.

**Gewenste situatie:** Robot bouwt een mental model van zijn omgeving, herkent kamers, en kan naar benoemde locaties navigeren.

**Waarom auto-discovery in plaats van pre-mapping:**
- Indrukwekkender/engagerender voor gebruiker
- Past zich aan wanneer meubels verplaatsen
- Sluit aan bij de "intelligent companion" visie
- Benut bestaande LLM + YOLO capabilities

---

## Hoe Past Dit in de Architectuur?

### Laag 1: Navigatie (Pi Lokaal)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ROOM DISCOVERY FLOW                           │
│                                                                      │
│  Camera Module 3                                                     │
│        │                                                             │
│        ▼                                                             │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐                 │
│  │ SLAM      │────►│ Frontier  │────►│ Navigate  │                 │
│  │ Mapping   │     │ Detection │     │ to Edge   │                 │
│  └───────────┘     └───────────┘     └───────────┘                 │
│        │                                    │                        │
│        │                                    │                        │
│        ▼                                    ▼                        │
│  ┌───────────┐                       ┌───────────┐                  │
│  │ Occupancy │                       │ Object    │◄── YOLO (Laag 0) │
│  │ Grid      │                       │ Detection │◄── VLM (Laag 2)  │
│  └───────────┘                       └───────────┘                  │
│        │                                    │                        │
│        └──────────────┬────────────────────┘                        │
│                       ▼                                              │
│                ┌─────────────┐                                       │
│                │ Semantic    │                                       │
│                │ Room Labels │                                       │
│                │ (waypoints) │                                       │
│                └─────────────┘                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Samenwerking met Andere Lagen

| Component | Laag | Rol |
|-----------|------|-----|
| SLAM/Mapping | 1 (lokaal) | Bouwt occupancy grid, tracked positie |
| Safety check | 0 (lokaal) | Voorkomt botsingen tijdens exploratie |
| Object detection | 0/2 | YOLO (lokaal) voor snelle detectie, VLM (remote) voor context |
| Room labeling | 2 (remote) | LLM bepaalt kamer type op basis van objecten |

---

## Core Capabilities

### 1. Visual SLAM Mapping
- Bouw occupancy grid met monoculaire camera
- Track robot positie binnen de kaart
- Detecteer wanneer je terugkeert bij bezochte gebieden (loop closure)

### 2. Frontier-Based Exploration
- Identificeer onverkende randen van de kaart ("frontiers")
- Navigeer autonoom naar frontiers
- Ga door tot omgeving volledig in kaart is gebracht

### 3. Semantic Room Labeling
- Gebruik YOLO (Laag 0) voor snelle object detectie (koelkast, bed, bank)
- Gebruik LLM/VLM (Laag 2) voor contextuel kamer identificatie
- Sla benoemde waypoints op met kaart coordinaten

### 4. Natural Language Navigation
- Nieuwe LLM tool: `navigate_to(location: string)`
- Lookup locatie in semantic map
- Path planning met obstacle avoidance (Laag 0)

---

## User Interactions

```
User: "Verken het huis"
Robot: Begint autonome exploratie, kondigt ontdekkingen aan
       "Ik heb gevonden wat lijkt op een keuken"
       "Er is een slaapkamer aan het einde van de gang"
       "Exploratie klaar. Ik heb 4 kamers in kaart gebracht."

User: "Rij naar de keuken"
Robot: Navigeert naar opgeslagen keuken waypoint

User: "Waar ben je?"
Robot: "Ik sta in de woonkamer, bij de bank"

User: "Welke kamers ken je?"
Robot: "Keuken, woonkamer, slaapkamer, en badkamer"
```

---

## Hardware

Zie [HARDWARE-REFERENCE.md](../hardware/HARDWARE-REFERENCE.md) voor de definitieve hardware configuratie.

**Relevante componenten voor deze feature:**

| Component | Rol | Status |
|-----------|-----|--------|
| Camera Module 3 (IMX708) | Visual SLAM input, object detectie | Te bestellen |
| ToF sensors (VL53L0X) | Zijwaartse afstandsmeting voor betere mapping | Besteld |
| Ultrasonic (HC-SR04) | Front obstacle detection + schaal calibratie | Geinstalleerd |

---

## Dependencies

- Monoculaire VSLAM library (ORB-SLAM3, RTAB-Map, of Stella-VSLAM)
- Path planning algoritme (A*, RRT, of Nav2)
- YOLO voor object detectie (al gepland voor Laag 0)
- LLM infrastructure (al geimplementeerd in Fase 1)

---

## Implementatie Roadmap

| Fase | Component | Status |
|------|-----------|--------|
| 3 | Camera Module 3 installeren | Gepland |
| 3 | YOLO nano safety layer | Gepland |
| 3 | (Optioneel) SLAM basis testen | Gepland |
| 4 | SLAM compleet integreren | Gepland |
| 4 | Frontier exploration | Gepland |
| 4 | Semantic room labeling | Gepland |
| 4 | navigate_to LLM tool | Gepland |

---

## Success Criteria

1. Robot kan multi-room omgeving zelfstandig verkennen
2. Identificeert en labelt correct minstens 3 kamer types
3. Navigeert succesvol naar benoemde kamers op voice command
4. Re-localiseert na verplaatst/uitgezet te zijn
5. Update kaart wanneer omgeving verandert

---

## Open Questions

- Kaarten persistent opslaan of herbouwen bij startup?
- Hoe om te gaan met meerdere verdiepingen?
- Moet robot ontdekkingen aankondigen of stil blijven tijdens exploratie?
- Integratie met toekomstige smart home features?

---

## Gerelateerde Ideeën (Future)

- **Patrol mode:** Periodieke autonome rondes voor beveiliging
- **Object memory:** "Waar heb ik mijn sleutels laatst gezien?"
- **Person following:** Volg een specifieke persoon
- **Return to charger:** Navigeer naar oplaadstation bij lage batterij

---

## Gerelateerde Documenten

- [4-layer-perception-architecture.md](4-layer-perception-architecture.md) - Architectuur waar deze feature in past
- [HARDWARE-REFERENCE.md](../hardware/HARDWARE-REFERENCE.md) - Definitieve hardware
- [fase4-autonomie/Fase4_Implementation_Plan.md](../../fase4-autonomie/Fase4_Implementation_Plan.md) - Fase waar dit wordt geimplementeerd
- [DECISIONS.md](../../DECISIONS.md) - D010 (Camera), D011 (4-laags architectuur)
