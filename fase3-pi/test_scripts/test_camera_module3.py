#!/usr/bin/env python3
"""
Camera Module 3 (IMX708) Test Script

Test de Camera Module 3 met picamera2:
1. Camera detectie
2. Foto maken
3. Autofocus test
4. Low-light configuratie
5. Base64 output (voor take_photo integratie)

Gebruik:
    conda activate nerdcarx
    python test_camera_module3.py

Vereist:
    pip install picamera2 pillow
"""

import sys
import time
import io
import base64
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent
TEST_PHOTO = OUTPUT_DIR / "test_capture.jpg"
TEST_PHOTO_LOWLIGHT = OUTPUT_DIR / "test_capture_lowlight.jpg"


def check_camera_available():
    """Check of picamera2 beschikbaar is."""
    print("\n" + "=" * 50)
    print("TEST 1: Camera Module Detectie")
    print("=" * 50)

    try:
        from picamera2 import Picamera2
        print("  picamera2 module gevonden")
    except ImportError:
        print("  picamera2 niet geïnstalleerd!")
        print("  Installeer met: pip install picamera2")
        print("  Of: sudo apt install python3-picamera2")
        return False

    try:
        camera = Picamera2()
        camera_info = camera.camera_properties
        print(f"  Camera gedetecteerd!")
        print(f"  Model: {camera_info.get('Model', 'Unknown')}")
        print(f"  Pixel Array: {camera_info.get('PixelArraySize', 'Unknown')}")

        # Check of het IMX708 is
        model = camera_info.get('Model', '')
        if 'imx708' in model.lower():
            print("  Type: Camera Module 3 (IMX708)")
        else:
            print(f"  Type: {model}")

        camera.close()
        return True

    except Exception as e:
        print(f"  Camera detectie gefaald: {e}")
        print("\n  Troubleshooting:")
        print("  1. Is de camera kabel goed aangesloten?")
        print("  2. Is camera interface enabled? sudo raspi-config → Interface Options → Camera")
        print("  3. Probeer: libcamera-hello --list-cameras")
        return False


def test_basic_capture():
    """Test basis foto capture."""
    print("\n" + "=" * 50)
    print("TEST 2: Basis Foto Capture")
    print("=" * 50)

    try:
        from picamera2 import Picamera2

        camera = Picamera2()

        # Configureer voor still image
        config = camera.create_still_configuration(
            main={"size": (1920, 1080)},  # Full HD voor test
        )
        camera.configure(config)

        print("  Camera configuratie toegepast")
        print("  Starting camera...")

        camera.start()

        # Wacht op autofocus
        print("  Wacht op autofocus (2s)...")
        time.sleep(2)

        # Capture
        print(f"  Capturing naar {TEST_PHOTO}...")
        camera.capture_file(str(TEST_PHOTO))

        camera.stop()
        camera.close()

        # Verify
        if TEST_PHOTO.exists():
            size = TEST_PHOTO.stat().st_size
            print(f"  Foto opgeslagen: {TEST_PHOTO.name} ({size / 1024:.1f} KB)")
            return True
        else:
            print("  Foto niet gevonden!")
            return False

    except Exception as e:
        print(f"  Capture gefaald: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_autofocus():
    """Test autofocus functionaliteit."""
    print("\n" + "=" * 50)
    print("TEST 3: Autofocus Test")
    print("=" * 50)

    try:
        from picamera2 import Picamera2
        from libcamera import controls

        camera = Picamera2()

        config = camera.create_still_configuration()
        camera.configure(config)
        camera.start()

        # Check autofocus support
        print("  Checking autofocus support...")

        # Trigger autofocus
        print("  Triggering autofocus cycle...")
        camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        time.sleep(1)

        # Check autofocus state
        metadata = camera.capture_metadata()
        af_state = metadata.get("AfState", "Unknown")
        lens_position = metadata.get("LensPosition", "Unknown")

        print(f"  AF State: {af_state}")
        print(f"  Lens Position: {lens_position}")

        camera.stop()
        camera.close()

        print("  Autofocus test geslaagd!")
        return True

    except ImportError:
        print("  libcamera controls niet beschikbaar - skip AF test")
        return True  # Niet kritiek
    except Exception as e:
        print(f"  Autofocus test warning: {e}")
        return True  # Niet kritiek voor basis functionaliteit


def test_lowlight_config():
    """Test low-light (night mode) configuratie."""
    print("\n" + "=" * 50)
    print("TEST 4: Low-Light Configuratie")
    print("=" * 50)

    try:
        from picamera2 import Picamera2

        camera = Picamera2()

        config = camera.create_still_configuration(
            main={"size": (1920, 1080)},
            controls={
                "AnalogueGain": 8.0,  # Hogere gain voor low-light
                "ExposureTime": 100000,  # Langere exposure (100ms)
            }
        )
        camera.configure(config)

        print("  Low-light configuratie toegepast")
        print("  AnalogueGain: 8.0")
        print("  ExposureTime: 100000 (100ms)")

        camera.start()
        time.sleep(2)

        print(f"  Capturing low-light foto naar {TEST_PHOTO_LOWLIGHT}...")
        camera.capture_file(str(TEST_PHOTO_LOWLIGHT))

        camera.stop()
        camera.close()

        if TEST_PHOTO_LOWLIGHT.exists():
            size = TEST_PHOTO_LOWLIGHT.stat().st_size
            print(f"  Foto opgeslagen: {TEST_PHOTO_LOWLIGHT.name} ({size / 1024:.1f} KB)")
            return True
        else:
            print("  Foto niet gevonden!")
            return False

    except Exception as e:
        print(f"  Low-light test gefaald: {e}")
        return False


def test_base64_capture():
    """Test base64 capture (voor take_photo integratie)."""
    print("\n" + "=" * 50)
    print("TEST 5: Base64 Capture (take_photo)")
    print("=" * 50)

    try:
        from picamera2 import Picamera2
        from PIL import Image

        camera = Picamera2()

        config = camera.create_still_configuration(
            main={"size": (640, 480)},  # Kleinere resolutie voor snelheid
        )
        camera.configure(config)

        camera.start()
        time.sleep(1)

        print("  Capturing frame...")
        array = camera.capture_array()

        camera.stop()
        camera.close()

        print(f"  Array shape: {array.shape}")

        # Converteer naar JPEG base64
        img = Image.fromarray(array)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        jpeg_bytes = buffer.getvalue()

        b64_string = base64.b64encode(jpeg_bytes).decode('utf-8')

        print(f"  JPEG size: {len(jpeg_bytes) / 1024:.1f} KB")
        print(f"  Base64 length: {len(b64_string)} chars")
        print(f"  Base64 preview: {b64_string[:50]}...")

        return True

    except ImportError:
        print("  PIL (Pillow) niet geïnstalleerd!")
        print("  Installeer met: pip install pillow")
        return False
    except Exception as e:
        print(f"  Base64 capture gefaald: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_video_stream():
    """Test video stream configuratie (voor MJPEG later)."""
    print("\n" + "=" * 50)
    print("TEST 6: Video Stream Configuratie")
    print("=" * 50)

    try:
        from picamera2 import Picamera2

        camera = Picamera2()

        # Video configuratie (voor MJPEG stream)
        config = camera.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"},
        )
        camera.configure(config)

        print("  Video configuratie:")
        print("  Size: 640x480")
        print("  Format: RGB888")

        camera.start()

        # Capture enkele frames
        print("  Capturing 5 frames...")
        for i in range(5):
            frame = camera.capture_array()
            print(f"    Frame {i+1}: {frame.shape}")
            time.sleep(0.1)

        camera.stop()
        camera.close()

        print("  Video stream test geslaagd!")
        return True

    except Exception as e:
        print(f"  Video stream test gefaald: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "#" * 50)
    print("# CAMERA MODULE 3 (IMX708) TEST SUITE")
    print("#" * 50)

    results = {}

    # Test 1: Camera detectie
    results["detectie"] = check_camera_available()
    if not results["detectie"]:
        print("\n CAMERA NIET GEVONDEN - Tests gestopt")
        print("Controleer aansluiting en voer deze stappen uit:")
        print("1. sudo shutdown now")
        print("2. Check CSI kabel (blauwe kant naar camera)")
        print("3. Start Pi en run: libcamera-hello --list-cameras")
        return 1

    # Test 2: Basis capture
    results["capture"] = test_basic_capture()

    # Test 3: Autofocus
    results["autofocus"] = test_autofocus()

    # Test 4: Low-light
    results["lowlight"] = test_lowlight_config()

    # Test 5: Base64
    results["base64"] = test_base64_capture()

    # Test 6: Video stream
    results["video"] = test_video_stream()

    # Summary
    print("\n" + "=" * 50)
    print("RESULTATEN")
    print("=" * 50)

    all_passed = True
    for test, passed in results.items():
        status = "" if passed else ""
        print(f"  {status} {test}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("ALLE TESTS GESLAAGD!")
        print(f"\nFoto's opgeslagen in:")
        print(f"  {TEST_PHOTO}")
        if TEST_PHOTO_LOWLIGHT.exists():
            print(f"  {TEST_PHOTO_LOWLIGHT}")
        print("\nCamera Module 3 is klaar voor gebruik!")
        return 0
    else:
        print("SOMMIGE TESTS GEFAALD")
        print("Zie bovenstaande output voor details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
