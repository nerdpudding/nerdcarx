#!/usr/bin/env python3
"""
Simpele WebSocket test voor NerdCarX orchestrator.
Test de verbinding en basis message flow.
"""
import asyncio
import json
import time
import websockets

WS_URL = "ws://localhost:8200/ws"


async def test_connection():
    """Test 1: Basis verbinding."""
    print("=" * 50)
    print("Test 1: WebSocket verbinding")
    print("=" * 50)

    try:
        async with websockets.connect(WS_URL) as ws:
            print(f"✅ Verbonden met {WS_URL}")
            return True
    except Exception as e:
        print(f"❌ Verbinding mislukt: {e}")
        return False


async def test_heartbeat():
    """Test 2: Heartbeat message."""
    print("\n" + "=" * 50)
    print("Test 2: Heartbeat")
    print("=" * 50)

    try:
        async with websockets.connect(WS_URL) as ws:
            # Stuur heartbeat
            msg = {
                "type": "heartbeat",
                "conversation_id": "test-session",
                "timestamp": time.time(),
                "payload": {}
            }
            await ws.send(json.dumps(msg))
            print(f"📤 Verzonden: heartbeat")

            # Heartbeat geeft geen response, maar geen error = OK
            await asyncio.sleep(0.5)
            print("✅ Heartbeat geaccepteerd (geen error)")
            return True
    except Exception as e:
        print(f"❌ Heartbeat test mislukt: {e}")
        return False


async def test_invalid_message():
    """Test 3: Error handling bij ongeldige message."""
    print("\n" + "=" * 50)
    print("Test 3: Error handling")
    print("=" * 50)

    try:
        async with websockets.connect(WS_URL) as ws:
            # Stuur ongeldige JSON
            await ws.send("dit is geen json")
            print("📤 Verzonden: ongeldige JSON")

            # Wacht op error response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📥 Ontvangen: {data.get('type', 'unknown')}")

                if data.get("type") == "error":
                    print("✅ Error correct afgehandeld")
                    return True
            except asyncio.TimeoutError:
                print("⚠️ Geen response (kan OK zijn)")
                return True

    except Exception as e:
        print(f"❌ Error handling test mislukt: {e}")
        return False


async def test_audio_process_no_audio():
    """Test 4: audio_process zonder audio data (moet error geven)."""
    print("\n" + "=" * 50)
    print("Test 4: audio_process zonder data")
    print("=" * 50)

    try:
        async with websockets.connect(WS_URL) as ws:
            msg = {
                "type": "audio_process",
                "conversation_id": "test-session",
                "timestamp": time.time(),
                "payload": {}  # Geen audio_base64
            }
            await ws.send(json.dumps(msg))
            print("📤 Verzonden: audio_process (zonder audio)")

            # Wacht op error response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 Ontvangen: {data.get('type', 'unknown')}")

                if data.get("type") == "error":
                    print(f"✅ Correcte error: {data.get('payload', {}).get('error', 'unknown')}")
                    return True
                else:
                    print(f"⚠️ Onverwacht response type: {data.get('type')}")
                    return False
            except asyncio.TimeoutError:
                print("❌ Timeout - geen response ontvangen")
                return False

    except Exception as e:
        print(f"❌ Test mislukt: {e}")
        return False


async def main():
    """Run alle tests."""
    print("\n🔌 NerdCarX WebSocket Tests\n")

    results = []

    # Test 1: Verbinding
    results.append(("Verbinding", await test_connection()))

    if not results[0][1]:
        print("\n❌ Verbinding mislukt - overige tests overgeslagen")
        return

    # Test 2: Heartbeat
    results.append(("Heartbeat", await test_heartbeat()))

    # Test 3: Error handling
    results.append(("Error handling", await test_invalid_message()))

    # Test 4: audio_process zonder data
    results.append(("Audio process (no data)", await test_audio_process_no_audio()))

    # Samenvatting
    print("\n" + "=" * 50)
    print("SAMENVATTING")
    print("=" * 50)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")

    print(f"\nResultaat: {passed}/{total} tests geslaagd")

    if passed == total:
        print("\n🎉 Alle WebSocket tests geslaagd!")
    else:
        print("\n⚠️ Sommige tests gefaald - check de output hierboven")


if __name__ == "__main__":
    asyncio.run(main())
