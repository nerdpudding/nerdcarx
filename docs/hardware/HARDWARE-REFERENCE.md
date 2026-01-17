# NerdCarX Hardware Reference

> **Last updated:** 2026-01-17
> **Hardware revision:** RobotHAT v4 + Pi 5

Dit document bevat de volledige hardware configuratie voor NerdCarX, inclusief pin mappings, I2C bus configuratie, en wiring instructies.

---

## Inhoudsopgave

1. [Hardware Inventory](#hardware-inventory)
2. [RobotHAT v4 Pin Mapping](#robothat-v4-pin-mapping)
3. [I2C Bus Configuratie](#i2c-bus-configuratie)
4. [Wiring Diagram](#wiring-diagram)
5. [Software Control](#software-control)
6. [Commissioning Checklist](#commissioning-checklist)

---

## Hardware Inventory

### Compute & Controller

| Component | Specificatie | Status |
|-----------|--------------|--------|
| Raspberry Pi 5 | 16GB RAM, Pi OS Lite (Trixie 64-bit) | Geïnstalleerd |
| RobotHAT v4 | SunFounder expansion board | Geïnstalleerd |
| Active Cooler | Pi 5 cooler | Geïnstalleerd |

### Sensoren

| Component | Interface | Pin/Bus | Status |
|-----------|-----------|---------|--------|
| Camera Module 3 (IMX708) | CSI | CSI port | **Besteld** |
| Camera OV5647 | CSI | CSI port | Geïnstalleerd (wordt vervangen) |
| Ultrasonic HC-SR04 | Digital | D2 (trig), D3 (echo) | Geïnstalleerd |
| Grayscale Module | ADC | A0, A1, A2 | Geïnstalleerd |
| 2x VL53L0X ToF | I2C via hub | CH0, CH1 | **Besteld** |

### Actuatoren

| Component | Interface | Pin | Status |
|-----------|-----------|-----|--------|
| DC Motors (2x) | Motor port | Motor1, Motor2 | Geïnstalleerd |
| Steering Servo | PWM | P2 | Geïnstalleerd |
| Camera Pan Servo | PWM | P0 | Geïnstalleerd |
| Camera Tilt Servo | PWM | P1 | Geïnstalleerd |

### Displays & Indicators

| Component | Interface | Pin/Address | Status |
|-----------|-----------|-------------|--------|
| OLED WPI438 (SSD1306) | I2C | 0x3C | ✅ Geïnstalleerd & werkend |
| 2x Grove LED (wit) | Digital | D0, D1 | **Besteld** |
| Battery LEDs (2x) | Onboard | - | Geïnstalleerd |

#### OLED Aansluiting Details

| OLED Pin | Kabelkleur | RobotHAT I2C Pin |
|----------|------------|------------------|
| VCC | Rood | 3V3 |
| GND | Grijs | GND |
| SCL | Geel | SCL |
| SDA | Groen | SDA |

De OLED is aangesloten op de **I2C Pin** header van de RobotHAT v4 (tussen Motor 1 en Motor 2 poorten).

### I2C Componenten

| Component | Address | Status |
|-----------|---------|--------|
| TCA9548A I2C Hub | 0x70 | **Besteld** |
| VL53L0X ToF (via hub) | 0x29 | **Besteld** |
| SSD1306 OLED | 0x3C | ✅ Werkend |

### Audio Hardware

| Component | Interface | Device | Status |
|-----------|-----------|--------|--------|
| USB Microfoon | USB Audio | Card 2, `plughw:2,0` | ✅ Werkend |
| I2S Speaker (mono) | I2S via RobotHAT | Card 3, `plughw:3,0` | ✅ Werkend |
| Amplifier Enable | GPIO | GPIO 20 | ✅ Werkend |

**Audio Configuratie Details:**

| Aspect | Waarde | Opmerking |
|--------|--------|-----------|
| Mic sample rate | 16kHz mono | Standaard voor STT |
| Mic gain | +20dB (software) | Via `sox` of Python (`audio * gain_factor`) |
| Speaker sample rate | 22.05kHz/44.1kHz | TTS output format |
| Amplifier enable | `pinctrl set 20 op dh` | Moet actief zijn voor speaker output |

**Test commando's:**
```bash
# Mic test (5 sec opname)
arecord -D plughw:2,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav

# Speaker test (activeer eerst amplifier!)
pinctrl set 20 op dh
aplay -D plughw:3,0 test.wav

# Mic volume op 100%
alsamixer -c 2  # F4 voor Capture, pijltjes omhoog

# Software gain toevoegen
sox input.wav output.wav gain 20
```

---

## RobotHAT v4 Pin Mapping

### Digital Pins (D0-D3)

| RobotHAT Pin | Raspberry Pi GPIO | Functie | Beschikbaar |
|--------------|-------------------|---------|-------------|
| D0 | GPIO17 | **LED Left** | ✅ Vrij |
| D1 | GPIO4 | **LED Right** | ✅ Vrij |
| D2 | GPIO27 | Ultrasonic TRIG | ❌ In gebruik |
| D3 | GPIO22 | Ultrasonic ECHO | ❌ In gebruik |

### ADC Pins (A0-A3)

| RobotHAT Pin | Functie | Beschikbaar |
|--------------|---------|-------------|
| A0 | Grayscale sensor | ❌ In gebruik |
| A1 | Grayscale sensor | ❌ In gebruik |
| A2 | Grayscale sensor | ❌ In gebruik |
| A3 | - | ✅ Vrij |
| A4 | Battery voltage (intern) | ❌ Gereserveerd |

### PWM Pins (P0-P11)

| RobotHAT Pin | Functie | Beschikbaar |
|--------------|---------|-------------|
| P0 | Camera Pan Servo | ❌ In gebruik |
| P1 | Camera Tilt Servo | ❌ In gebruik |
| P2 | Steering Servo | ❌ In gebruik |
| P3-P11 | - | ✅ Vrij |
| P12 | Motor2 PWM (intern) | ❌ Gereserveerd |
| P13 | Motor1 PWM (intern) | ❌ Gereserveerd |

### I2C Bus

| Signal | Raspberry Pi GPIO | Connector |
|--------|-------------------|-----------|
| SDA | GPIO2 | P2.54 4-pin of SH1.0 (QWIIC) |
| SCL | GPIO3 | P2.54 4-pin of SH1.0 (QWIIC) |

### Motor Ports

| Port | Direction GPIO | PWM Channel |
|------|----------------|-------------|
| Motor1 (Left) | GPIO23 | PWM13 |
| Motor2 (Right) | GPIO24 | PWM12 |

### Overige Pins

| Functie | GPIO |
|---------|------|
| User LED | GPIO26 |
| USR Button | GPIO25 |
| RST Button | GPIO16 |
| MCU Reset | GPIO5 |

---

## I2C Bus Configuratie

### Bus Topologie

```
Raspberry Pi I2C-1 (Bus 1)
│
│  SDA = GPIO2
│  SCL = GPIO3
│  Pull-up: 10K (onboard RobotHAT)
│
├─────────────────────────────────────┐
│                                     │
│                                     │
▼                                     ▼
┌──────────────────┐         ┌──────────────────┐
│ OLED Display     │         │ TCA9548A Hub     │
│ SSD1306          │         │ I2C Multiplexer  │
│ Address: 0x3C    │         │ Address: 0x70    │
│                  │         │                  │
│ VCC: 3.3V/5V     │         │ VCC: 3.3V/5V     │
│ GND: GND         │         │ GND: GND         │
│ SDA: GPIO2       │         │ SDA: GPIO2       │
│ SCL: GPIO3       │         │ SCL: GPIO3       │
└──────────────────┘         └────────┬─────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                  ┌──────────────┐         ┌──────────────┐
                  │ Channel 0    │         │ Channel 1    │
                  │              │         │              │
                  │ VL53L0X ToF  │         │ VL53L0X ToF  │
                  │ LEFT         │         │ RIGHT        │
                  │ Address: 0x29│         │ Address: 0x29│
                  └──────────────┘         └──────────────┘
```

### Waarom TCA9548A Hub?

De VL53L0X ToF sensoren hebben een **vast I2C adres (0x29)** dat niet kan worden gewijzigd. Om twee identieke sensoren te gebruiken, schakelen we via de TCA9548A hub tussen kanalen. De hub zelf heeft adres **0x70**.

### Verwachte I2C Adressen

| Scan Moment | Verwachte Adressen |
|-------------|-------------------|
| Na boot (zonder hub select) | 0x3C (OLED), 0x70 (TCA hub) |
| Na `tca_select(0)` | 0x29 (ToF left) |
| Na `tca_select(1)` | 0x29 (ToF right) |

---

## Wiring Diagram

### Fysieke Aansluitingen

```
┌─────────────────────────────────────────────────────────────────┐
│                        ROBOTHAT V4 (TOP VIEW)                    │
│                                                                  │
│  DIGITAL PINS                    I2C CONNECTORS                  │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐    ┌──────────────────────┐   │
│  │ D0  │ │ D1  │ │ D2  │ │ D3  │    │ I2C P2.54 (4-pin)    │   │
│  │     │ │     │ │     │ │     │    │ VCC SDA SCL GND      │   │
│  │ LED │ │ LED │ │ US  │ │ US  │    └──────────────────────┘   │
│  │ L   │ │ R   │ │TRIG │ │ECHO │                                │
│  └──┬──┘ └──┬──┘ └─────┘ └─────┘    ┌──────────────────────┐   │
│     │       │                        │ I2C SH1.0 (QWIIC)    │   │
│     │       │                        └──────────────────────┘   │
└─────┼───────┼────────────────────────────────────────────────────┘
      │       │
      │       │  Grove→Dupont adapters
      │       │
      ▼       ▼
┌─────────┐ ┌─────────┐
│Grove LED│ │Grove LED│
│  LEFT   │ │  RIGHT  │
└─────────┘ └─────────┘


I2C BUS WIRING:

RobotHAT I2C ────┬──────────────────────────┐
                 │                          │
                 ▼                          ▼
          ┌──────────┐              ┌──────────────┐
          │  OLED    │              │  TCA9548A    │
          │  WPI438  │              │  Hub         │
          └──────────┘              └──────┬───────┘
                                           │
                              ┌────────────┼────────────┐
                              │            │            │
                              ▼            ▼            ▼
                         ┌────────┐  ┌────────┐   (CH2-7 unused)
                         │ToF L   │  │ToF R   │
                         │(CH0)   │  │(CH1)   │
                         └────────┘  └────────┘
```

### Kabels Nodig

| Van | Naar | Kabel Type |
|-----|------|------------|
| RobotHAT D0 | Grove LED Left | Grove→Dupont female |
| RobotHAT D1 | Grove LED Right | Grove→Dupont female |
| RobotHAT I2C | OLED WPI438 | Dupont female-female 4-wire |
| RobotHAT I2C | TCA9548A Hub IN | Grove of Dupont 4-wire |
| TCA9548A CH0 | ToF Left | Grove cable |
| TCA9548A CH1 | ToF Right | Grove cable |

---

## Software Control

### I2C Hub Channel Select

```python
import smbus2

TCA_ADDR = 0x70  # TCA9548A default address
bus = smbus2.SMBus(1)  # I2C bus 1

def tca_select(channel: int):
    """Select TCA9548A channel (0-7)."""
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be 0-7")
    bus.write_byte(TCA_ADDR, 1 << channel)

def tca_disable():
    """Disable all TCA9548A channels."""
    bus.write_byte(TCA_ADDR, 0)
```

### ToF Sensor Reading

```python
import VL53L0X  # pip install VL53L0X

# Initialize ToF (after tca_select!)
tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)

def read_tof_left() -> int:
    """Read left ToF distance in mm."""
    tca_select(0)
    tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
    distance = tof.get_distance()
    tof.stop_ranging()
    return distance

def read_tof_right() -> int:
    """Read right ToF distance in mm."""
    tca_select(1)
    tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
    distance = tof.get_distance()
    tof.stop_ranging()
    return distance
```

### LED Control

```python
from robot_hat import Pin

led_left = Pin("D0")
led_right = Pin("D1")

def set_leds(left: bool, right: bool):
    """Set LED states."""
    led_left.value(1 if left else 0)
    led_right.value(1 if right else 0)

def obstacle_warning(left_dist: int, right_dist: int, threshold: int = 200):
    """Flash LEDs based on ToF distance."""
    set_leds(
        left=left_dist < threshold,
        right=right_dist < threshold
    )
```

### OLED Display

```python
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

# Initialize OLED (direct on bus, no hub select needed)
serial = i2c(port=1, address=0x3C)
oled = ssd1306(serial)

def show_status(text: str):
    """Display text on OLED."""
    with canvas(oled) as draw:
        draw.text((0, 0), text, fill="white")

def show_distances(left: int, right: int):
    """Show ToF distances on OLED."""
    with canvas(oled) as draw:
        draw.text((0, 0), f"L: {left}mm", fill="white")
        draw.text((0, 16), f"R: {right}mm", fill="white")
```

### Complete Sensor Loop Example

```python
import time

def sensor_loop():
    """Main sensor reading loop."""
    while True:
        # Read ToF sensors
        dist_left = read_tof_left()
        dist_right = read_tof_right()

        # Read ultrasonic (existing)
        from picarx import Picarx
        px = Picarx()
        dist_front = px.get_distance()

        # Update LEDs based on side distances
        obstacle_warning(dist_left, dist_right, threshold=200)

        # Update OLED
        show_distances(dist_left, dist_right)

        # Safety check
        if dist_left < 100 or dist_right < 100 or dist_front < 20:
            px.stop()
            print("Obstacle detected!")

        time.sleep(0.1)
```

---

## Commissioning Checklist

### 1. I2C Bus Verificatie

```bash
# Scan I2C bus (verwacht: 0x3C OLED, 0x70 TCA hub)
i2cdetect -y 1

# Verwachte output:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 70: 70 -- -- -- -- -- -- --
```

### 2. ToF Sensor Test

```python
# Test ToF via hub channels
import smbus2

bus = smbus2.SMBus(1)
TCA_ADDR = 0x70
TOF_ADDR = 0x29

# Select channel 0, check for ToF
bus.write_byte(TCA_ADDR, 1 << 0)
try:
    bus.read_byte(TOF_ADDR)
    print("ToF Left found on CH0")
except:
    print("ToF Left NOT found!")

# Select channel 1, check for ToF
bus.write_byte(TCA_ADDR, 1 << 1)
try:
    bus.read_byte(TOF_ADDR)
    print("ToF Right found on CH1")
except:
    print("ToF Right NOT found!")
```

### 3. LED Test

```python
from robot_hat import Pin
import time

led_left = Pin("D0")
led_right = Pin("D1")

# Blink test
for _ in range(3):
    led_left.value(1)
    led_right.value(0)
    time.sleep(0.5)
    led_left.value(0)
    led_right.value(1)
    time.sleep(0.5)

# Off
led_left.value(0)
led_right.value(0)
print("LED test complete")
```

### 4. OLED Test

```python
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

serial = i2c(port=1, address=0x3C)
oled = ssd1306(serial)

with canvas(oled) as draw:
    draw.rectangle(oled.bounding_box, outline="white", fill="black")
    draw.text((10, 25), "NerdCarX", fill="white")

print("OLED test complete - check display")
```

---

## Troubleshooting

### I2C Device Not Found

1. Check wiring (SDA/SCL not swapped)
2. Check power (3.3V or 5V depending on module)
3. Check pull-up resistors (RobotHAT has 10K onboard)
4. Try lower I2C speed: `sudo nano /boot/config.txt` → `dtparam=i2c_baudrate=50000`

### ToF Sensor Not Responding via Hub

1. Verify hub is detected (`i2cdetect -y 1` shows 0x70)
2. Check Grove cable connection to correct hub channel
3. Try different hub channel
4. Verify ToF power (needs 2.8V-5V)

### LED Not Lighting

1. Check Grove→Dupont adapter orientation
2. Verify D0/D1 pin connection (not D2/D3)
3. Test with `Pin("D0").value(1)` in Python REPL
4. Check LED polarity

---

## References

- [SunFounder RobotHAT v4 Documentation](https://docs.sunfounder.com/projects/robot-hat/en/latest/)
- [SunFounder PiCar-X Documentation](https://docs.sunfounder.com/projects/picar-x/en/latest/)
- [VL53L0X Datasheet](https://www.st.com/resource/en/datasheet/vl53l0x.pdf)
- [TCA9548A Datasheet](https://www.ti.com/lit/ds/symlink/tca9548a.pdf)
- [SSD1306 OLED Datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf)
