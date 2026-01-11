#!/usr/bin/env python3
"""
Test Fish Audio parameters - very_consistent vs ultra_consistent
Met realistische conversatie voorbeelden
"""

import time
import subprocess
import requests

API_URL = "http://localhost:8250/v1/tts"
REFERENCE_ID = "dutch2"

def play_audio(filename):
    """Speel audio af"""
    print(f"  >>> Afspelen...")
    subprocess.run(["aplay", "-q", filename], check=True)

# Realistische conversatie zinnen (kort -> lang)
test_sentences = [
    ("heel_kort", "Ja hoor!"),
    ("kort", "Hallo, hoe gaat het?"),
    ("normaal", "Ik ben NerdCarX, je persoonlijke assistent."),
    ("medium", "Het weer is vandaag erg mooi, met zo'n twintig graden en zon."),
    ("lang", "Ik zie twee golden retriever puppies die vrolijk door het park rennen op deze zonnige dag."),
    ("vraag", "Wil je dat ik je help met het zoeken naar informatie?"),
    ("uitleg", "Om dat te doen moet je eerst naar het menu gaan, dan op instellingen klikken en vervolgens de optie aanpassen."),
]

# Alleen de beste twee configuraties
configs = [
    {"name": "very_consistent", "temperature": 0.3, "top_p": 0.6},
    {"name": "ultra_consistent", "temperature": 0.2, "top_p": 0.5},
]

print("=" * 70)
print("FISH AUDIO - VERY vs ULTRA CONSISTENT")
print("Reference: dutch2 (ElevenLabs NL vrouw)")
print("=" * 70)

for config in configs:
    name = config["name"]
    temp = config["temperature"]
    top_p = config["top_p"]

    print(f"\n{'='*70}")
    print(f"CONFIG: {name.upper()} (temp={temp}, top_p={top_p})")
    print("=" * 70)

    total_time = 0

    for i, (label, text) in enumerate(test_sentences, 1):
        print(f"\n[{i}/{len(test_sentences)}] {label.upper()}")
        print(f"  \"{text}\"")
        print(f"  Genereren...", end=" ", flush=True)

        t_start = time.perf_counter()

        response = requests.post(
            API_URL,
            json={
                "text": text,
                "reference_id": REFERENCE_ID,
                "temperature": temp,
                "top_p": top_p,
                "format": "wav"
            },
            timeout=30
        )

        latency = (time.perf_counter() - t_start) * 1000
        total_time += latency

        if response.status_code == 200:
            filename = f"test_{name}_{label}.wav"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"{latency:.0f}ms ({len(text)} chars)")
            play_audio(filename)
        else:
            print(f"ERROR: {response.status_code}")

    avg_time = total_time / len(test_sentences)
    print(f"\n  Gemiddelde latency: {avg_time:.0f}ms")

print("\n" + "=" * 70)
print("VERGELIJKING")
print("=" * 70)

print("\nLuister nogmaals naar specifieke zinnen:")
print("\n  VERY_CONSISTENT:")
for label, _ in test_sentences:
    print(f"    aplay test_very_consistent_{label}.wav")

print("\n  ULTRA_CONSISTENT:")
for label, _ in test_sentences:
    print(f"    aplay test_ultra_consistent_{label}.wav")

print("\n" + "=" * 70)
print("BEOORDELING")
print("=" * 70)
print("""
Let op:
  - Uitspraak van 'gaat', 'graden', 'vrolijk'
  - Natuurlijke intonatie bij vragen
  - Consistentie tussen korte en lange zinnen

Welke klinkt beter: very_consistent of ultra_consistent?
""")
