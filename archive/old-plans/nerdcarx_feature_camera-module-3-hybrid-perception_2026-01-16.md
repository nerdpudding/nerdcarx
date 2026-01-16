# Plan: Camera Module 3 + Hybride Perceptie Architectuur

**Datum:** 2026-01-16
**Status:** Klaar voor implementatie

---

## Samenvatting

Camera Module 3 bestellen en architectuur voorbereiden op hybride perceptie (lokaal safety + remote GPU). Dit wijkt niet af van het huidige faseplan, maar voegt toekomstgerichte uitbreidingen toe.

**Uitvoering vandaag:**
1. Documentatie nu bijwerken (dit plan)
2. Later vandaag: Fase 1 TODO afronden
3. Camera Module 3 bestellen
4. Daarna: Fase 2 → Fase 3 (met optioneel SLAM)

---

## Wat Wordt Gedocumenteerd

### 4-Laags Perceptie Architectuur

| Laag | Doel | Locatie | Latency | Fase |
|------|------|---------|---------|------|
| **0 Safety** | Niet botsen, obstacle avoidance | Pi lokaal | <50ms | 3 |
| **1 Navigatie** | Route planning, SLAM | Pi lokaal | Real-time | 3 (optioneel) / 4 |
| **2 Perceptie** | Pose, VLM, heavy detection | Desktop GPU | ~200ms OK | 4+ |
| **3 Conversatie** | STT→LLM→TTS | Desktop | Niet kritisch | 1-3 |

### Camera Module 3 Keuze

| Aspect | Camera Module 3 (IMX708) | AI Camera (IMX500) |
|--------|--------------------------|-------------------|
| Flexibiliteit | ✅ Elk model, waar je wilt | Model lock-in |
| Features | HDR, autofocus, 12MP | On-camera inference |
| Geschikt voor | Lokaal + remote dual use | Specifiek edge AI |
| Prijs | ~€25 | ~€70 |

**Conclusie:** CM3 past beter bij hybride aanpak met zware GPU op desktop.

### Dual Vision Pad
```
Camera Module 3
      │
      ├──► [Pi lokaal] YOLO nano → Safety/obstacle (Laag 0)
      │
      └──► [Stream ~200ms] → Desktop GPU → Pose/VLM (Laag 2)
```

---

## Bestanden om Bij te Werken

### 1. Feature Proposal (NIEUW)
**Bestand:** `docs/feature-proposals/hybrid-perception-camera-module-3.md`

Bevat:
- 4-laags architectuur uitleg
- Camera Module 3 rationale
- Dual vision pad diagram
- Relatie met autonomous-room-discovery.md
- Hardware requirements
- Implementatie notities per fase

### 2. DECISIONS.md (UPDATE)
Toevoegen:
- **D010**: Camera Module 3 keuze (IMX708 vervangt OV5647)
- **D011**: 4-laags perceptie architectuur

### 3. ARCHITECTURE.md (UPDATE)
Sectie 6 (Container View):
- Dual vision pad toevoegen aan Phase 3 diagram
- Laag 0/1/2/3 uitleg toevoegen

Sectie 11 (Future Possibilities):
- SLAM/navigatie concreter maken
- Pose detectie use cases noemen

Hardware Requirements:
- Camera Module 3 als "gepland" toevoegen

### 4. fase3-pi/PLAN.md (UPDATE)
Toevoegen:
- Camera Module 3 in hardware checklist
- Streaming naar desktop als optionele taak
- YOLO safety layer taken
- SLAM als "optioneel, afhankelijk van timing"

### 5. fase4-autonomie/PLAN.md (UPDATE)
Toevoegen:
- Link naar autonomous-room-discovery.md
- SLAM expliciet noemen als onderdeel
- Pose detectie use cases

### 6. README.md (UPDATE)
- Hardware status: Camera Module 3 gepland
- Fase beschrijvingen verduidelijken

---

## Verificatie

Na implementatie checken:
- [ ] Feature proposal bevat complete rationale
- [ ] DECISIONS.md heeft D010 en D011
- [ ] ARCHITECTURE.md toont dual vision pad
- [ ] Fase 3 plan noemt Camera Module 3 en optioneel SLAM
- [ ] Fase 4 plan linkt naar room discovery
- [ ] README reflecteert nieuwe hardware plannen
- [ ] Geen duplicate informatie tussen documenten
- [ ] Structuur blijft overzichtelijk
