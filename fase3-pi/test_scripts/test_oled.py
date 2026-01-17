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

    print(f"✅ OLED gevonden en geïnitialiseerd!")
    print(f"   Resolutie: {device.width}x{device.height}")

    # Toon tekst op display
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((10, 20), "Hello", fill="white")
        draw.text((10, 35), "NerdCarX!", fill="white")

    print("✅ Tekst weergegeven op display!")
    print("\n👀 Kijk naar het OLED scherm!")
    print("\nDruk Ctrl+C om te stoppen en scherm te wissen...")

    # Houd display aan
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    # Clear display bij exit
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, fill="black")
    print("\n✅ Display gewist. Klaar!")

except Exception as e:
    print(f"❌ Fout: {e}")
    print("\nTroubleshooting:")
    print("1. Check of OLED op 0x3C zit: i2cdetect -y 1")
    print("2. Installeer library: pip install luma.oled")
