#!/usr/bin/env python3
"""
OLED Emotie Demo met Geanimeerde Gezichtjes
NerdCarX - 128x64 OLED (SSD1306)
"""

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageDraw
import time
import math

# OLED setup
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Display dimensies
WIDTH = 128
HEIGHT = 64
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2 - 5  # Iets omhoog voor tekst onderaan


class Face:
    """Tekent een gezicht met ogen en mond."""

    # Oog posities
    LEFT_EYE_X = CENTER_X - 25
    RIGHT_EYE_X = CENTER_X + 25
    EYE_Y = CENTER_Y - 8

    # Mond positie
    MOUTH_Y = CENTER_Y + 15

    @staticmethod
    def draw_eyes(draw, left_open=True, right_open=True, eye_style="normal"):
        """Tekent de ogen."""
        lx, rx, y = Face.LEFT_EYE_X, Face.RIGHT_EYE_X, Face.EYE_Y

        if eye_style == "normal":
            # Ronde ogen
            if left_open:
                draw.ellipse([lx-10, y-10, lx+10, y+10], outline="white", fill="white")
                draw.ellipse([lx-4, y-4, lx+4, y+4], outline="black", fill="black")  # Pupil
            else:
                draw.line([lx-10, y, lx+10, y], fill="white", width=2)

            if right_open:
                draw.ellipse([rx-10, y-10, rx+10, y+10], outline="white", fill="white")
                draw.ellipse([rx-4, y-4, rx+4, y+4], outline="black", fill="black")  # Pupil
            else:
                draw.line([rx-10, y, rx+10, y], fill="white", width=2)

        elif eye_style == "happy":
            # Blije ogen (omgekeerde U)
            draw.arc([lx-10, y-5, lx+10, y+15], 0, 180, fill="white", width=2)
            draw.arc([rx-10, y-5, rx+10, y+15], 0, 180, fill="white", width=2)

        elif eye_style == "sad":
            # Droevige ogen (tranen)
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
                # Simpel hartje met twee cirkels en driehoek
                draw.ellipse([ex-10, y-10, ex-2, y-2], outline="white", fill="white")
                draw.ellipse([ex+2, y-10, ex+10, y-2], outline="white", fill="white")
                draw.polygon([(ex-10, y-5), (ex+10, y-5), (ex, y+10)], fill="white")

        elif eye_style == "tired":
            # Half gesloten ogen
            draw.arc([lx-10, y-5, lx+10, y+10], 0, 180, fill="white", width=2)
            draw.arc([rx-10, y-5, rx+10, y+10], 0, 180, fill="white", width=2)

        elif eye_style == "curious":
            # Een oog groter dan ander
            draw.ellipse([lx-12, y-12, lx+12, y+12], outline="white", fill="white")
            draw.ellipse([lx-4, y-4, lx+4, y+4], outline="black", fill="black")
            draw.ellipse([rx-8, y-8, rx+8, y+8], outline="white", fill="white")
            draw.ellipse([rx-3, y-3, rx+3, y+3], outline="black", fill="black")
            # Opgetrokken wenkbrauw
            draw.arc([lx-15, y-25, lx+15, y-10], 200, 340, fill="white", width=2)

    @staticmethod
    def draw_mouth(draw, mouth_style="neutral"):
        """Tekent de mond."""
        mx, my = CENTER_X, Face.MOUTH_Y

        if mouth_style == "neutral":
            draw.line([mx-15, my, mx+15, my], fill="white", width=2)

        elif mouth_style == "happy":
            # Grote glimlach
            draw.arc([mx-20, my-15, mx+20, my+10], 20, 160, fill="white", width=2)

        elif mouth_style == "very_happy":
            # Open mond glimlach
            draw.arc([mx-20, my-10, mx+20, my+15], 0, 180, fill="white", width=2)
            draw.line([mx-18, my-2, mx+18, my-2], fill="white", width=1)

        elif mouth_style == "sad":
            # Omgekeerde glimlach
            draw.arc([mx-15, my-5, mx+15, my+15], 200, 340, fill="white", width=2)

        elif mouth_style == "very_sad":
            # Trilllende onderlip
            draw.arc([mx-18, my-5, mx+18, my+12], 200, 340, fill="white", width=2)
            draw.arc([mx-12, my+5, mx+12, my+15], 20, 160, fill="white", width=1)

        elif mouth_style == "angry":
            # Strakke mond, iets naar beneden
            draw.line([mx-12, my-3, mx, my+2], fill="white", width=2)
            draw.line([mx, my+2, mx+12, my-3], fill="white", width=2)

        elif mouth_style == "surprised":
            # Open O mond
            draw.ellipse([mx-10, my-8, mx+10, my+8], outline="white", fill="white")
            draw.ellipse([mx-5, my-3, mx+5, my+3], outline="black", fill="black")

        elif mouth_style == "love":
            # Kusmondje
            draw.ellipse([mx-6, my-6, mx+6, my+6], outline="white", fill="white")

        elif mouth_style == "tired":
            # Open geeuw
            draw.ellipse([mx-8, my-10, mx+8, my+6], outline="white", fill="white")


def draw_label(draw, text):
    """Tekent emotie naam onderaan."""
    # Simpele centrering
    text_width = len(text) * 6  # Geschatte breedte
    x = (WIDTH - text_width) // 2
    draw.text((x, HEIGHT - 12), text, fill="white")


def show_emotion(emotion, duration=2.0, animate=True):
    """Toont een emotie met optionele animatie."""

    emotions_config = {
        "happy": {"eyes": "happy", "mouth": "very_happy", "label": "HAPPY"},
        "sad": {"eyes": "sad", "mouth": "very_sad", "label": "SAD"},
        "angry": {"eyes": "angry", "mouth": "angry", "label": "ANGRY"},
        "surprised": {"eyes": "surprised", "mouth": "surprised", "label": "SURPRISED"},
        "neutral": {"eyes": "normal", "mouth": "neutral", "label": "NEUTRAL"},
        "love": {"eyes": "love", "mouth": "love", "label": "LOVE"},
        "tired": {"eyes": "tired", "mouth": "tired", "label": "TIRED"},
        "curious": {"eyes": "curious", "mouth": "neutral", "label": "CURIOUS"},
        "excited": {"eyes": "surprised", "mouth": "very_happy", "label": "EXCITED"},
        "shy": {"eyes": "normal", "mouth": "happy", "label": "SHY"},
        "confused": {"eyes": "curious", "mouth": "neutral", "label": "CONFUSED"},
        "proud": {"eyes": "happy", "mouth": "happy", "label": "PROUD"},
        "worried": {"eyes": "sad", "mouth": "sad", "label": "WORRIED"},
        "bored": {"eyes": "tired", "mouth": "neutral", "label": "BORED"},
        "thinking": {"eyes": "normal", "mouth": "neutral", "label": "THINKING"},
    }

    config = emotions_config.get(emotion, emotions_config["neutral"])

    if animate and emotion in ["happy", "excited", "love"]:
        # Blije animatie - knipperende ogen
        for _ in range(2):
            # Ogen open
            with canvas(device) as draw:
                Face.draw_eyes(draw, True, True, config["eyes"])
                Face.draw_mouth(draw, config["mouth"])
                draw_label(draw, config["label"])
            time.sleep(0.3)
            # Knipoog
            with canvas(device) as draw:
                Face.draw_eyes(draw, False, False, "normal")
                Face.draw_mouth(draw, config["mouth"])
                draw_label(draw, config["label"])
            time.sleep(0.1)
        # Eind frame
        with canvas(device) as draw:
            Face.draw_eyes(draw, True, True, config["eyes"])
            Face.draw_mouth(draw, config["mouth"])
            draw_label(draw, config["label"])
        time.sleep(duration - 0.8)

    elif animate and emotion == "sad":
        # Droevige animatie - langzaam knipperen
        with canvas(device) as draw:
            Face.draw_eyes(draw, True, True, config["eyes"])
            Face.draw_mouth(draw, config["mouth"])
            draw_label(draw, config["label"])
        time.sleep(duration * 0.7)
        # Langzaam ogen dicht
        with canvas(device) as draw:
            Face.draw_eyes(draw, False, False, "normal")
            Face.draw_mouth(draw, config["mouth"])
            draw_label(draw, config["label"])
        time.sleep(duration * 0.3)

    elif animate and emotion == "thinking":
        # Thinking animatie - ogen naar links/rechts
        for i in range(3):
            with canvas(device) as draw:
                # Shift pupils
                lx, rx, y = Face.LEFT_EYE_X, Face.RIGHT_EYE_X, Face.EYE_Y
                offset = 4 if i % 2 == 0 else -4
                # Ogen
                draw.ellipse([lx-10, y-10, lx+10, y+10], outline="white", fill="white")
                draw.ellipse([lx-4+offset, y-4, lx+4+offset, y+4], outline="black", fill="black")
                draw.ellipse([rx-10, y-10, rx+10, y+10], outline="white", fill="white")
                draw.ellipse([rx-4+offset, y-4, rx+4+offset, y+4], outline="black", fill="black")
                Face.draw_mouth(draw, config["mouth"])
                draw_label(draw, config["label"])
            time.sleep(0.5)

    else:
        # Statisch
        with canvas(device) as draw:
            Face.draw_eyes(draw, True, True, config["eyes"])
            Face.draw_mouth(draw, config["mouth"])
            draw_label(draw, config["label"])
        time.sleep(duration)


def demo():
    """Demo van alle emoties."""
    print("OLED Emotie Demo")
    print("=" * 40)
    print("Ctrl+C om te stoppen\n")

    emotions = [
        "neutral", "happy", "excited", "love", "proud",
        "curious", "thinking", "surprised",
        "tired", "bored", "shy",
        "sad", "worried", "confused", "angry"
    ]

    try:
        while True:
            for emotion in emotions:
                print(f"  -> {emotion}")
                show_emotion(emotion, duration=2.5, animate=True)
                time.sleep(0.3)
            print("\n  [Opnieuw...]\n")

    except KeyboardInterrupt:
        # Clear display
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, fill="black")
        print("\n\nDemo gestopt. Display gewist.")


if __name__ == "__main__":
    demo()
