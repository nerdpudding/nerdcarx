# Fase 4: Vision

**Status:** Gepland
**Doel:** Camera input voor context-aware interactie
**Afhankelijk van:** Fase 3 (Pi Integratie)

## Overzicht

Deze fase activeert de camera op de Pi zodat de robot visueel kan waarnemen. Ministral ondersteunt multimodale input (tekst + images), dus we hoeven alleen de camera pipeline toe te voegen.

Er zijn twee vision capabilities:
1. **LLM Vision**: Diepgaande analyse via Ministral ("beschrijf wat je ziet")
2. **Object Detection**: Snelle labels via YOLO op Pi ("persoon gedetecteerd")

## Taken

### Camera Basis
- [ ] Camera module installeren (picamera2)
- [ ] Test scripts voor foto's maken
- [ ] JPEG compressie configureren
- [ ] Camera integreren in Pi Client

### LLM Vision (Ministral)
- [ ] Image meesturen in request naar orchestrator
- [ ] Orchestrator stuurt image naar Ministral
- [ ] Vision-gerelateerde vragen testen
- [ ] Latency optimaliseren (image size, quality)

### Object Detection op Pi (Optioneel - Fase 4b)
- [ ] YOLO Nano/Small installeren (ultralytics)
- [ ] Continuous detection loop
- [ ] Detection results als metadata
- [ ] Triggers voor proactief gedrag

### Vision Commands
- [ ] "Wat zie je?" commando
- [ ] "Kijk naar me" commando
- [ ] Gezichtsuitdrukking analyse
- [ ] Object beschrijving

## Architectuur

### LLM Vision Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  User: "Wat zie je?"                                                │
│                                                                      │
│  Pi:                                                                │
│  ┌────────────────┐                                                 │
│  │ Camera Capture │ → JPEG (compressed)                             │
│  └────────────────┘                                                 │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ Request: { audio: ..., image: <jpeg>, conversation_id } │        │
│  └─────────────────────────────────────────────────────────┘        │
│                             │                                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Desktop Orchestrator:                                               │
│                                                                      │
│  STT: "Wat zie je?"                                                 │
│           │                                                          │
│           ▼                                                          │
│  Ministral: [text: "Wat zie je?", image: <jpeg>]                    │
│           │                                                          │
│           ▼                                                          │
│  Response: "Ik zie een bureau met een laptop en koffiemok..."       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Object Detection Flow (Fase 4b)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Pi - Continuous Detection:                                          │
│                                                                      │
│  Camera → YOLO (Nano) → Detections                                  │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────┐          │
│  │ Detections: [                                          │          │
│  │   {label: "person", confidence: 0.94, bbox: [...]},   │          │
│  │   {label: "laptop", confidence: 0.87, bbox: [...]}    │          │
│  │ ]                                                      │          │
│  └───────────────────────────────────────────────────────┘          │
│                              │                                       │
│                              ▼                                       │
│  Trigger: Nieuwe persoon gedetecteerd?                              │
│           → Proactieve melding                                       │
│                                                                      │
│  Request: Metadata meesturen als context                            │
│           → LLM krijgt zowel image ALS gestructureerde labels       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Use Cases

### UC4: Visuele Analyse op Verzoek
```
User: "Beschrijf wat je ziet"
→ Camera snapshot
→ Ministral analyseert image + vraag
→ "Ik zie een bureau met een monitor en toetsenbord..."
```

### UC5: Gezichtsuitdrukking Analyse
```
User: "Hoe kijk ik?"
→ Camera snapshot (gezicht)
→ Ministral analyseert gezichtsuitdrukking
→ "Je kijkt geconcentreerd. Druk bezig?"
→ OLED spiegelt expressie
```

### UC6: Object Detection Trigger (Proactief)
```
YOLO detecteert: "person" appeared (was niet in beeld)
→ Trigger naar orchestrator
→ LLM genereert reactie
→ "Iemand is binnengekomen"
→ OLED: alert emotie
```

### UC7: Gecombineerde Metadata + Vision
```
User: "Wat staat er op mijn bureau?"
→ Image + YOLO metadata: [laptop, cup, book]
→ Ministral: image voor details, metadata voor snelle context
→ "Op je bureau zie ik een laptop, kopje, en notitieboek"
```

## Camera Configuratie

```python
# picamera2 voorbeeld
from picamera2 import Picamera2

camera = Picamera2()
config = camera.create_still_configuration(
    main={"size": (640, 480)},  # Balans kwaliteit/latency
    buffer_count=2
)
camera.configure(config)

def capture_jpeg():
    return camera.capture_array("main")
```

## Image Optimalisatie

| Aspect | Waarde | Reden |
|--------|--------|-------|
| Resolutie | 640x480 | Balans detail/snelheid |
| Format | JPEG | Kleinere payload |
| Quality | 75-85% | Acceptabele compressie |
| Max size | ~100KB | Network friendly |

## YOLO op Pi (Fase 4b)

```python
from ultralytics import YOLO

# Nano model voor snelheid op Pi
model = YOLO("yolov8n.pt")  # of yolo11n.pt

def detect(frame):
    results = model(frame, verbose=False)
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                "label": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy[0].tolist()
            })
    return detections
```

## Success Criteria

| Criterium | Test |
|-----------|------|
| Camera capture werkt | Foto's maken op commando |
| LLM vision werkt | "Wat zie je?" geeft correcte beschrijving |
| Gezichtsanalyse | "Hoe kijk ik?" detecteert expressie |
| Latency acceptabel | < 1.5 sec met image |
| YOLO werkt (4b) | Detecteert personen/objecten realtime |

## Voortgang

| Datum | Update |
|-------|--------|
| - | Fase nog niet gestart |

## Notities

*Voeg hier notities, learnings en beslissingen toe tijdens de implementatie*

---

[← Fase 3](../3.fase3-pi-integratie/FASE3-PLAN.md) | [Terug naar README](../README.md) | [Volgende: Fase 5 →](../5.fase5-autonomie/FASE5-PLAN.md)
