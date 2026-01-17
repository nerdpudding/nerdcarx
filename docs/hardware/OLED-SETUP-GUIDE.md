# OLED Display Aansluiten - Stap voor Stap

> **Display:** Whadda WPI438 (SSD1306, 128x64, I2C, blauw)
> **Doel:** Emoties tonen op NerdCarX robot

---

## Wat heb je nodig?

- [x] OLED display WPI438 (4 pinnen: VCC, GND, SCL, SDA)
- [x] 4x Female-to-female dupont kabels
- [x] Raspberry Pi 5 met RobotHAT v4 (al geïnstalleerd)

---

## Stap 1: Pi UITZETTEN

**BELANGRIJK:** Zet de Pi UIT voordat je kabels aansluit!

```bash
# Op de Pi (via SSH of terminal)
sudo shutdown now
```

Wacht tot het groene lampje op de Pi stopt met knipperen (±10 seconden).

**Waarom?** I2C devices kunnen beschadigd raken als je ze "hot plug" aansluit terwijl de Pi aan staat.

---

## Stap 2: Kabels Aansluiten

### De 4 pinnen op de OLED

Kijk naar je OLED display. Je ziet 4 pinnen met labels:

```
OLED Display (voorkant naar je toe)
┌─────────────────────┐
│                     │
│   [OLED SCHERM]     │
│                     │
└─────────────────────┘
    │  │  │  │
   VCC GND SCL SDA
```

### Waar aansluiten op RobotHAT?

De RobotHAT heeft een **I2C connector** (4-pins). Deze zit meestal aan de bovenkant van de HAT, gelabeld "I2C" of met de pin namen.

```
RobotHAT I2C Connector (4-pin header)
┌─────────────────────┐
│  VCC  SDA  SCL  GND │   ← Controleer labels op jouw HAT!
└─────────────────────┘
```

**LET OP:** De volgorde kan verschillen per HAT versie. Kijk ALTIJD naar de labels op de HAT zelf!

### Aansluiting tabel

| OLED Pin | Kleur kabel | RobotHAT Pin |
|----------|-------------|--------------|
| **VCC**  | **Rood**    | **3V3** |
| **GND**  | **Grijs**   | **GND** |
| **SCL**  | **Geel**    | **SCL** |
| **SDA**  | **Groen**   | **SDA** |

> **Note:** Dit zijn de kleuren zoals gebruikt in de NerdCarX opstelling.

### Visueel schema

```
OLED Display                    RobotHAT I2C Pin Header
    │                                  │
   VCC ──────── ROOD ─────────────── 3V3
   GND ──────── GRIJS ────────────── GND
   SCL ──────── GEEL ─────────────── SCL
   SDA ──────── GROEN ────────────── SDA
```

### Tips voor aansluiten

1. **Gebruik verschillende kleuren** - Maakt troubleshooten makkelijker
2. **Controleer VOOR aanzetten** - Verkeerde aansluiting kan display kapot maken
3. **Niet forceren** - Dupont kabels moeten makkelijk op de pinnen schuiven

---

## Stap 3: Pi Aanzetten

1. Zet de Pi aan (stroom aansluiten of power button)
2. Wacht tot Pi volledig is opgestart (±30-60 seconden)
3. SSH naar de Pi:

```bash
ssh rvanpolen@192.168.1.71
# of
ssh rvanpolen@nerdcarx.local
```

---

## Stap 4: Controleren of OLED Gevonden Wordt

### I2C bus scannen

```bash
# Installeer i2c-tools als nog niet aanwezig
sudo apt install -y i2c-tools

# Scan de I2C bus
i2cdetect -y 1
```

### Verwachte output (OLED aangesloten)

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

**Succes!** `3c` = het OLED display is gevonden op adres 0x3C

### Probleem: Geen 3c zichtbaar?

| Probleem | Oplossing |
|----------|-----------|
| Helemaal geen output | I2C niet enabled? `sudo raspi-config` → Interface Options → I2C → Enable |
| Alleen `70` zichtbaar | Dat is de I2C hub (TCA9548A) - OLED kabels zitten verkeerd |
| Helemaal niets | Controleer VCC/GND niet verwisseld, kabels goed aangesloten |

---

## Stap 5: Test Script Draaien

### Dependencies installeren

```bash
# Activeer conda environment
conda activate nerdcarx

# Installeer luma.oled library
pip install luma.oled
```

### Simpel test script maken

```bash
# Maak test script
cat > ~/test_oled.py << 'EOF'
#!/usr/bin/env python3
"""
OLED Display Test Script
Toont "Hello NerdCarX!" op het display
"""

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
import time

print("OLED Test Script")
print("=" * 40)

try:
    # Verbind met OLED op I2C bus 1, adres 0x3C
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial)

    print("✅ OLED gevonden en geïnitialiseerd!")
    print(f"   Resolutie: {device.width}x{device.height}")

    # Toon tekst op display
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((10, 25), "Hello", fill="white")
        draw.text((10, 40), "NerdCarX!", fill="white")

    print("✅ Tekst weergegeven op display!")
    print("\n👀 Kijk naar het OLED scherm - je zou moeten zien:")
    print('   "Hello"')
    print('   "NerdCarX!"')
    print("\nDruk Ctrl+C om te stoppen...")

    # Houd display aan
    while True:
        time.sleep(1)

except Exception as e:
    print(f"❌ Fout: {e}")
    print("\nTroubleshooting:")
    print("1. Check of OLED op 0x3C zit: i2cdetect -y 1")
    print("2. Check kabels: VCC→VCC, GND→GND, SCL→SCL, SDA→SDA")
    print("3. Check of I2C enabled is: sudo raspi-config")
EOF

# Maak uitvoerbaar
chmod +x ~/test_oled.py
```

### Script uitvoeren

```bash
conda activate nerdcarx
python ~/test_oled.py
```

### Verwacht resultaat

**In terminal:**
```
OLED Test Script
========================================
✅ OLED gevonden en geïnitialiseerd!
   Resolutie: 128x64
✅ Tekst weergegeven op display!

👀 Kijk naar het OLED scherm - je zou moeten zien:
   "Hello"
   "NerdCarX!"

Druk Ctrl+C om te stoppen...
```

**Op het OLED display:**
```
┌──────────────────────┐
│                      │
│      Hello           │
│      NerdCarX!       │
│                      │
└──────────────────────┘
```

---

## Stap 6: Geavanceerde Test (Emoties)

Als de basis test werkt, probeer dit:

```bash
cat > ~/test_oled_emotions.py << 'EOF'
#!/usr/bin/env python3
"""
OLED Emotie Test - Toont verschillende emoties
"""

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont
import time

# Emotie emoji's (tekst-based voor nu)
EMOTIONS = {
    "happy":    ("^_^", "HAPPY"),
    "sad":      ("T_T", "SAD"),
    "angry":    (">_<", "ANGRY"),
    "neutral":  ("-_-", "NEUTRAL"),
    "surprised":("O_O", "SURPRISED"),
    "love":     ("<3_<3", "LOVE"),
    "curious":  ("?_?", "CURIOUS"),
    "tired":    ("=_=", "TIRED"),
}

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

print("Emotie demo - Ctrl+C om te stoppen")

try:
    for emotion, (face, name) in EMOTIONS.items():
        print(f"  Showing: {emotion}")

        with canvas(device) as draw:
            # Grote emotie face in het midden
            draw.text((40, 15), face, fill="white")
            # Emotie naam onderaan
            draw.text((35, 50), name, fill="white")

        time.sleep(2)

except KeyboardInterrupt:
    pass

# Clear display
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, fill="black")

print("Done!")
EOF

python ~/test_oled_emotions.py
```

---

## Troubleshooting

### Display toont niets

1. **Contrast te laag?** Display werkt maar is niet zichtbaar
   ```python
   device.contrast(255)  # Max contrast
   ```

2. **Verkeerde driver?** WPI438 gebruikt SSD1306, sommige displays gebruiken SH1106
   ```python
   # Probeer alternatieve driver
   from luma.oled.device import sh1106
   device = sh1106(serial)
   ```

### "Permission denied" error

```bash
# Voeg user toe aan i2c groep
sudo usermod -aG i2c $USER
# Log opnieuw in
exit
# SSH opnieuw
```

### "No module named luma" error

```bash
conda activate nerdcarx
pip install luma.oled
```

---

## Volgende Stappen

Na succesvolle test:

1. **Integratie met NerdCarX** - `show_emotion` function call koppelen aan OLED
2. **Emotie assets** - Grafische emotie gezichten maken (optioneel)
3. **Pi client uitbreiden** - OLED handler toevoegen

Zie: [Fase3_Implementation_Plan.md](../../fase3-pi/Fase3_Implementation_Plan.md#subfase-3b-oled-emotie-display-later)

---

## Quick Reference

| Commando | Doel |
|----------|------|
| `i2cdetect -y 1` | Check of OLED gevonden wordt (zoek 3c) |
| `python ~/test_oled.py` | Basis display test |
| `python ~/test_oled_emotions.py` | Emotie demo |

| OLED Pin | RobotHAT Pin | GPIO |
|----------|--------------|------|
| VCC | VCC | - |
| GND | GND | - |
| SCL | SCL | GPIO3 |
| SDA | SDA | GPIO2 |

---

*Laatst bijgewerkt: 2026-01-17*
