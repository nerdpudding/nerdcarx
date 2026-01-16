# Plan: Hardware Documentatie + Camera Module 3 Architectuur

**Datum:** 2026-01-16
**Status:** Klaar voor implementatie

---

## Samenvatting

1. **Hardware documentatie toevoegen** - Volledige pin mapping, I2C setup, ToF sensors, LEDs
2. **Camera Module 3 architectuur** - Hybride perceptie (lokaal safety + remote GPU)

Dit is de definitieve hardware configuratie - LiDAR is out of scope (te duur/veel stroom).

**Uitvoering vandaag:**
1. Hardware documentatie toevoegen aan project
2. Camera Module 3 + perceptie architectuur documenteren (al gedaan)
3. Later: Fase 1 TODO afronden
4. Daarna: Fase 2 → Fase 3

---

## DEEL 1: Hardware Documentatie (NIEUW)

### Geverifieerde Pin Mapping (RobotHAT v4)

| Pin | GPIO | Huidig Gebruik | Beschikbaar |
|-----|------|----------------|-------------|
| D0 | GPIO17 | - | ✅ **LED Left** |
| D1 | GPIO4 | - | ✅ **LED Right** |
| D2 | GPIO27 | Ultrasonic TRIG | ❌ |
| D3 | GPIO22 | Ultrasonic ECHO | ❌ |
| A0-A2 | ADC | Grayscale sensor | ❌ |
| A3 | ADC | - | ✅ Vrij |
| P0-P2 | PWM | Servo's (pan/tilt/steer) | ❌ |
| P3-P11 | PWM | - | ✅ Vrij |
| I2C | GPIO2/3 | - | ✅ **OLED + TCA9548A** |

### I2C Bus Configuratie

```
Raspberry Pi I2C-1 (GPIO2 SDA, GPIO3 SCL)
           │
           ├── OLED Display (SSD1306) @ 0x3C
           │
           └── TCA9548A I2C Multiplexer @ 0x70
                    │
                    ├── CH0: VL53L0X ToF Left @ 0x29
                    │
                    └── CH1: VL53L0X ToF Right @ 0x29
```

### Nieuwe Hardware Inventory

| Component | Interface | Status |
|-----------|-----------|--------|
| Camera Module 3 (IMX708) | CSI | Te bestellen |
| OLED WPI438 (SSD1306) | I2C direct | Aanwezig |
| TCA9548A I2C Hub | I2C direct | Besteld |
| 2x VL53L0X ToF Sensors | I2C via hub | Besteld |
| 2x Grove LED (wit) | D0, D1 | Besteld |
| Grove kabels | - | Besteld |

### Wiring Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      ROBOTHAT V4                             │
│                                                              │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐            │
│  │ D0     │  │ D1     │  │ D2     │  │ D3     │            │
│  │ LED L  │  │ LED R  │  │ US TRG │  │ US ECH │            │
│  └────────┘  └────────┘  └────────┘  └────────┘            │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ I2C Bus (P2.54 or SH1.0/QWIIC)                      │   │
│  │ SDA=GPIO2, SCL=GPIO3                                │   │
│  └──────────────────┬──────────────────────────────────┘   │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
  ┌──────────┐              ┌──────────────┐
  │ OLED     │              │ TCA9548A Hub │
  │ SSD1306  │              │ @ 0x70       │
  │ @ 0x3C   │              └──────┬───────┘
  └──────────┘                     │
                          ┌────────┴────────┐
                          │                 │
                          ▼                 ▼
                    ┌──────────┐      ┌──────────┐
                    │ ToF Left │      │ ToF Right│
                    │ VL53L0X  │      │ VL53L0X  │
                    │ CH0      │      │ CH1      │
                    └──────────┘      └──────────┘
```

### Software Control (pseudocode - geverifieerd)

```python
# I2C Hub channel select
TCA_ADDR = 0x70
def tca_select(channel):  # channel 0-7
    smbus.write_byte(TCA_ADDR, 1 << channel)

# ToF reading
def read_tof_left():
    tca_select(0)
    return vl53l0x.read_mm()

def read_tof_right():
    tca_select(1)
    return vl53l0x.read_mm()

# LEDs via robot_hat Pin class
from robot_hat import Pin
led_left = Pin("D0")
led_right = Pin("D1")
led_left.value(1)  # ON
led_right.value(0) # OFF
```

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

## DEEL 2: Bestanden om Bij te Werken

### 1. Hardware Reference Document (NIEUW)
**Bestand:** `docs/hardware/HARDWARE-REFERENCE.md`

Bevat:
- Volledige pin mapping (D0-D3, A0-A3, P0-P11, I2C)
- I2C bus configuratie met diagram
- Wiring instructies voor alle componenten
- Software control voorbeelden
- Commissioning checklist

### 2. Feature Proposal - Hybrid Perception (AL GEDAAN)
**Bestand:** `docs/feature-proposals/hybrid-perception-camera-module-3.md`
✅ Aangemaakt in vorige sessie

### 3. DECISIONS.md (UPDATE)
Toevoegen:
- **D010**: Camera Module 3 (AL GEDAAN)
- **D011**: 4-laags perceptie (AL GEDAAN)
- **D012**: Hardware uitbreiding (ToF, LEDs, OLED, I2C hub)

### 4. ARCHITECTURE.md (UPDATE)
- Hardware sectie uitbreiden met I2C configuratie
- ToF sensors en LEDs toevoegen aan sensor overzicht

### 5. fase3-pi/PLAN.md (UPDATE)
Toevoegen:
- Volledige hardware checklist (ToF, LEDs, OLED)
- I2C commissioning taken
- LED indicator taken

### 6. README.md (UPDATE)
- Hardware status: ToF sensors, LEDs besteld
- Link naar hardware reference

---

## Verificatie

Na implementatie checken:
- [ ] `docs/hardware/HARDWARE-REFERENCE.md` bevat volledige pin mapping
- [ ] DECISIONS.md heeft D010, D011, en D012
- [ ] ARCHITECTURE.md toont I2C configuratie
- [ ] Fase 3 plan heeft volledige hardware checklist
- [ ] README reflecteert bestelde hardware
- [ ] Geen duplicate informatie tussen documenten

## Commissioning Checklist (voor wanneer hardware binnen is)

```bash
# 1. I2C scan (verwacht: 0x3C OLED, 0x70 TCA hub)
i2cdetect -y 1

# 2. Test OLED
# (python script met luma.oled)

# 3. Test ToF via hub
# Select CH0, scan, verwacht 0x29
# Select CH1, scan, verwacht 0x29

# 4. Test LEDs
from robot_hat import Pin
Pin("D0").value(1)  # LED links aan
Pin("D1").value(1)  # LED rechts aan
```
