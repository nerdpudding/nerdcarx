#!/usr/bin/env python3
"""
OLED Display Module voor NerdCarX
Toont emotie gezichten op 128x64 SSD1306 OLED

Gebruik:
    from oled_display import OLEDDisplay

    display = OLEDDisplay()
    display.show_emotion("happy")
    display.clear()
"""

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
import time
import threading

# Display dimensies
WIDTH = 128
HEIGHT = 64
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2


class OLEDDisplay:
    """OLED display controller voor emotie gezichten."""

    # Oog posities
    LEFT_EYE_X = CENTER_X - 25
    RIGHT_EYE_X = CENTER_X + 25
    EYE_Y = CENTER_Y - 8

    # Mond positie
    MOUTH_Y = CENTER_Y + 18

    def __init__(self, address=0x3C, port=1):
        """Initialiseer OLED display."""
        try:
            serial = i2c(port=port, address=address)
            self.device = ssd1306(serial)
            self.available = True
            self.current_emotion = "neutral"
            self._animation_stop = threading.Event()
        except Exception as e:
            print(f"[OLED] Niet beschikbaar: {e}")
            self.available = False
            self.device = None

    def _draw_eyes(self, draw, eye_style="normal", blink=False):
        """Tekent de ogen."""
        lx, rx, y = self.LEFT_EYE_X, self.RIGHT_EYE_X, self.EYE_Y

        if blink:
            # Gesloten ogen
            draw.line([lx-10, y, lx+10, y], fill="white", width=2)
            draw.line([rx-10, y, rx+10, y], fill="white", width=2)
            return

        if eye_style == "normal":
            # Ronde ogen met pupil
            draw.ellipse([lx-10, y-10, lx+10, y+10], outline="white", fill="white")
            draw.ellipse([lx-4, y-4, lx+4, y+4], outline="black", fill="black")
            draw.ellipse([rx-10, y-10, rx+10, y+10], outline="white", fill="white")
            draw.ellipse([rx-4, y-4, rx+4, y+4], outline="black", fill="black")

        elif eye_style == "happy":
            # Blije ogen (omgekeerde U)
            draw.arc([lx-10, y-5, lx+10, y+15], 0, 180, fill="white", width=3)
            draw.arc([rx-10, y-5, rx+10, y+15], 0, 180, fill="white", width=3)

        elif eye_style == "sad":
            # Droevige ogen met tranen
            draw.ellipse([lx-8, y-8, lx+8, y+8], outline="white", fill="white")
            draw.ellipse([lx-3, y-3, lx+3, y+3], outline="black", fill="black")
            draw.ellipse([rx-8, y-8, rx+8, y+8], outline="white", fill="white")
            draw.ellipse([rx-3, y-3, rx+3, y+3], outline="black", fill="black")
            # Tranen
            draw.ellipse([lx+12, y+5, lx+16, y+15], outline="white", fill="white")
            draw.ellipse([rx+12, y+5, rx+16, y+15], outline="white", fill="white")

        elif eye_style == "angry":
            # Boze ogen met wenkbrauwen
            draw.ellipse([lx-8, y-6, lx+8, y+8], outline="white", fill="white")
            draw.ellipse([lx-3, y-2, lx+3, y+4], outline="black", fill="black")
            draw.ellipse([rx-8, y-6, rx+8, y+8], outline="white", fill="white")
            draw.ellipse([rx-3, y-2, rx+3, y+4], outline="black", fill="black")
            # Boze wenkbrauwen
            draw.line([lx-12, y-15, lx+8, y-8], fill="white", width=3)
            draw.line([rx+12, y-15, rx-8, y-8], fill="white", width=3)

        elif eye_style == "surprised":
            # Grote ronde ogen
            draw.ellipse([lx-14, y-14, lx+14, y+14], outline="white", fill="white")
            draw.ellipse([lx-5, y-5, lx+5, y+5], outline="black", fill="black")
            draw.ellipse([rx-14, y-14, rx+14, y+14], outline="white", fill="white")
            draw.ellipse([rx-5, y-5, rx+5, y+5], outline="black", fill="black")

        elif eye_style == "love":
            # Hartjes ogen
            for ex in [lx, rx]:
                draw.ellipse([ex-10, y-10, ex-2, y-2], outline="white", fill="white")
                draw.ellipse([ex+2, y-10, ex+10, y-2], outline="white", fill="white")
                draw.polygon([(ex-10, y-5), (ex+10, y-5), (ex, y+10)], fill="white")

        elif eye_style == "tired":
            # Half gesloten ogen
            draw.arc([lx-10, y-5, lx+10, y+10], 0, 180, fill="white", width=3)
            draw.arc([rx-10, y-5, rx+10, y+10], 0, 180, fill="white", width=3)

        elif eye_style == "curious":
            # Een oog groter dan ander
            draw.ellipse([lx-12, y-12, lx+12, y+12], outline="white", fill="white")
            draw.ellipse([lx-4, y-4, lx+4, y+4], outline="black", fill="black")
            draw.ellipse([rx-8, y-8, rx+8, y+8], outline="white", fill="white")
            draw.ellipse([rx-3, y-3, rx+3, y+3], outline="black", fill="black")
            # Opgetrokken wenkbrauw
            draw.arc([lx-15, y-25, lx+15, y-10], 200, 340, fill="white", width=2)

    def _draw_mouth(self, draw, mouth_style="neutral"):
        """Tekent de mond."""
        mx, my = CENTER_X, self.MOUTH_Y

        if mouth_style == "neutral":
            draw.line([mx-15, my, mx+15, my], fill="white", width=2)

        elif mouth_style == "happy":
            draw.arc([mx-20, my-15, mx+20, my+10], 20, 160, fill="white", width=3)

        elif mouth_style == "very_happy":
            draw.arc([mx-22, my-10, mx+22, my+15], 0, 180, fill="white", width=2)
            draw.line([mx-20, my-2, mx+20, my-2], fill="white", width=1)

        elif mouth_style == "sad":
            draw.arc([mx-15, my-5, mx+15, my+15], 200, 340, fill="white", width=3)

        elif mouth_style == "very_sad":
            draw.arc([mx-18, my-5, mx+18, my+12], 200, 340, fill="white", width=3)

        elif mouth_style == "angry":
            draw.line([mx-12, my-3, mx, my+2], fill="white", width=3)
            draw.line([mx, my+2, mx+12, my-3], fill="white", width=3)

        elif mouth_style == "surprised":
            draw.ellipse([mx-10, my-8, mx+10, my+8], outline="white", fill="white")
            draw.ellipse([mx-5, my-3, mx+5, my+3], outline="black", fill="black")

        elif mouth_style == "love":
            draw.ellipse([mx-6, my-6, mx+6, my+6], outline="white", fill="white")

        elif mouth_style == "tired":
            draw.ellipse([mx-8, my-10, mx+8, my+6], outline="white", fill="white")

    def _draw_face(self, draw, eye_style, mouth_style, blink=False):
        """Tekent een volledig gezicht."""
        self._draw_eyes(draw, eye_style, blink)
        self._draw_mouth(draw, mouth_style)

    def show_emotion(self, emotion: str, animate: bool = True):
        """
        Toon een emotie op het display.

        Args:
            emotion: Een van de 15 emoties (happy, sad, angry, etc.)
            animate: Of er een korte animatie getoond moet worden
        """
        if not self.available:
            return

        self.current_emotion = emotion
        self._animation_stop.clear()

        # Emotie configuratie
        config = {
            "happy":     {"eyes": "happy", "mouth": "very_happy"},
            "sad":       {"eyes": "sad", "mouth": "very_sad"},
            "angry":     {"eyes": "angry", "mouth": "angry"},
            "surprised": {"eyes": "surprised", "mouth": "surprised"},
            "neutral":   {"eyes": "normal", "mouth": "neutral"},
            "love":      {"eyes": "love", "mouth": "love"},
            "tired":     {"eyes": "tired", "mouth": "tired"},
            "curious":   {"eyes": "curious", "mouth": "neutral"},
            "excited":   {"eyes": "surprised", "mouth": "very_happy"},
            "shy":       {"eyes": "normal", "mouth": "happy"},
            "confused":  {"eyes": "curious", "mouth": "sad"},
            "proud":     {"eyes": "happy", "mouth": "happy"},
            "worried":   {"eyes": "sad", "mouth": "sad"},
            "bored":     {"eyes": "tired", "mouth": "neutral"},
            "thinking":  {"eyes": "normal", "mouth": "neutral"},
        }.get(emotion, {"eyes": "normal", "mouth": "neutral"})

        eye_style = config["eyes"]
        mouth_style = config["mouth"]

        if animate and emotion in ["happy", "excited", "love"]:
            # Blije animatie - snel knipperen
            for _ in range(2):
                if self._animation_stop.is_set():
                    break
                with canvas(self.device) as draw:
                    self._draw_face(draw, eye_style, mouth_style, blink=False)
                time.sleep(0.2)
                with canvas(self.device) as draw:
                    self._draw_face(draw, eye_style, mouth_style, blink=True)
                time.sleep(0.1)

        # Toon finale gezicht
        with canvas(self.device) as draw:
            self._draw_face(draw, eye_style, mouth_style, blink=False)

    def clear(self):
        """Wis het display."""
        if not self.available:
            return
        self._animation_stop.set()
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, fill="black")

    def show_startup(self):
        """Toon startup animatie."""
        if not self.available:
            return
        # Ogen langzaam open
        for i in range(3):
            with canvas(self.device) as draw:
                y = self.EYE_Y
                lx, rx = self.LEFT_EYE_X, self.RIGHT_EYE_X
                size = 3 + i * 4
                draw.ellipse([lx-size, y-size, lx+size, y+size], outline="white", fill="white")
                draw.ellipse([rx-size, y-size, rx+size, y+size], outline="white", fill="white")
            time.sleep(0.15)
        time.sleep(0.2)
        self.show_emotion("happy", animate=False)

    def show_sleep(self):
        """Toon slaap gezicht (gesloten ogen)."""
        if not self.available:
            return
        with canvas(self.device) as draw:
            # Gesloten ogen (Z z z)
            lx, rx, y = self.LEFT_EYE_X, self.RIGHT_EYE_X, self.EYE_Y
            draw.line([lx-10, y, lx+10, y], fill="white", width=2)
            draw.line([rx-10, y, rx+10, y], fill="white", width=2)
            # Z's voor slapen
            draw.text((rx+20, y-15), "Z", fill="white")
            draw.text((rx+28, y-25), "z", fill="white")
            draw.text((rx+34, y-32), "z", fill="white")


# Test
if __name__ == "__main__":
    display = OLEDDisplay()

    if display.available:
        print("OLED Display Test")
        print("=" * 40)

        display.show_startup()
        time.sleep(1)

        emotions = ["happy", "sad", "angry", "surprised", "love", "tired", "curious", "neutral"]

        for emotion in emotions:
            print(f"  {emotion}")
            display.show_emotion(emotion)
            time.sleep(1.5)

        display.show_sleep()
        time.sleep(1.5)

        display.clear()
        print("Klaar!")
    else:
        print("OLED niet beschikbaar")
