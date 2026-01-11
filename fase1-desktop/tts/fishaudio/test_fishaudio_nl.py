#!/usr/bin/env python3
"""
Test Fish Audio S1-mini - Nederlands + Latency Benchmark
Vergelijk met Chatterbox (5000-20000ms)

Vereist: Fish Audio server draaiend op localhost:8080
"""

import time
import requests

API_URL = "http://localhost:8250/v1/tts"

def generate_speech(text: str, filename: str) -> float:
    """Generate speech and return latency in ms"""
    t_start = time.perf_counter()

    response = requests.post(
        API_URL,
        json={"text": text, "format": "wav"},
        timeout=30
    )

    latency_ms = (time.perf_counter() - t_start) * 1000

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return latency_ms
    else:
        print(f"  ERROR: {response.status_code} - {response.text}")
        return -1

# Check server health
print("Checking Fish Audio server...")
try:
    health = requests.get("http://localhost:8250/v1/health", timeout=5)
    if health.status_code != 200:
        print("ERROR: Server not healthy")
        exit(1)
    print("Server OK\n")
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to http://localhost:8250")
    print("Start server first with:")
    print("  docker run --gpus device=0 --name fish-tts -v $(pwd)/checkpoints:/app/checkpoints -e COMPILE=1 -p 8250:8080 fishaudio/fish-speech python -m tools.api_server --listen 0.0.0.0:8080")
    exit(1)

# Warmup
print("Warmup (eerste call is traag door compile)...")
warmup_latency = generate_speech("Test warmup.", "warmup.wav")
print(f"Warmup done: {warmup_latency:.0f}ms\n")

# Test Nederlandse zinnen
texts = [
    ("kort", "Hallo, ik ben NerdCarX."),
    ("medium", "Hoe kan ik je vandaag helpen met je vraag?"),
    ("lang", "Ik zie twee golden retriever puppies in een bloemenveld op een zonnige dag met een heldere blauwe lucht."),
    ("emotie", "(excited) Wat leuk dat je er bent! Ik ben zo blij!"),
]

print("=" * 60)
print("FISH AUDIO S1-MINI NEDERLANDS TEST + BENCHMARK")
print("=" * 60)

results = []

for i, (label, text) in enumerate(texts, 1):
    print(f"\n[{label.upper()}] {text[:60]}{'...' if len(text) > 60 else ''}")

    # 3 runs voor benchmark
    times = []
    for run in range(3):
        filename = f"test_nl_{i}.wav"
        latency = generate_speech(text, filename)
        if latency > 0:
            times.append(latency)

    if times:
        avg = sum(times) / len(times)
        results.append((label, len(text), avg))
        print(f"  Latency: {avg:.0f}ms (min:{min(times):.0f} max:{max(times):.0f})")
        print(f"  Saved:   test_nl_{i}.wav")
    else:
        print(f"  FAILED")

print("\n" + "=" * 60)
print("SAMENVATTING")
print("=" * 60)

print("\nFish Audio S1-mini:")
for label, chars, avg in results:
    print(f"  {label:8s}: {avg:6.0f}ms ({chars} chars)")

print("\nChatterbox (ter vergelijking):")
print("  kort    :  ~5000ms")
print("  medium  : ~10000ms")
print("  lang    : ~20000ms")

if results:
    total_avg = sum(r[2] for r in results) / len(results)
    print("\n" + "=" * 60)
    if total_avg < 500:
        print(f"VERDICT: Fish Audio is ~{5000/total_avg:.0f}x sneller dan Chatterbox!")
        print("         Geweldig! Vervang Chatterbox.")
    elif total_avg < 1000:
        print(f"VERDICT: {total_avg:.0f}ms gemiddeld - acceptabel")
        print("         Beter dan Chatterbox, overweeg vervanging.")
    else:
        print(f"VERDICT: {total_avg:.0f}ms gemiddeld - te traag")
        print("         Probeer Piper als backup.")
    print("=" * 60)

print("\nLuister met:")
for i in range(1, len(texts) + 1):
    print(f"  aplay test_nl_{i}.wav")

print("\nBeoordeel:")
print("  - Is het Nederlands verstaanbaar?")
print("  - Klinkt het natuurlijk?")
print("  - Werkt de emotie marker?")
