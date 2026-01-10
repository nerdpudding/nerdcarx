#!/usr/bin/env python3
"""
Test Voxtral transcriptie.

Gebruik:
    python3 test_transcription.py <audio_file> [language]

Voorbeelden:
    python3 test_transcription.py ../test-audio/obama.mp3 en
    python3 test_transcription.py mijn_audio.wav nl
"""

import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package niet geïnstalleerd.")
    print("Run: pip install openai")
    sys.exit(1)


def transcribe(audio_path: str, language: str = "en") -> dict:
    """Transcribeer audio bestand via Voxtral."""

    client = OpenAI(
        base_url="http://localhost:8150/v1",
        api_key="dummy"  # vLLM vereist geen echte key
    )

    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio bestand niet gevonden: {audio_path}")

    print(f"Transcriberen: {audio_file.name}")
    print(f"Taal: {language}")
    print("-" * 40)

    start_time = time.time()

    with open(audio_file, "rb") as f:
        response = client.audio.transcriptions.create(
            model="RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic",
            file=f,
            language=language,
            temperature=0.0
        )

    elapsed = time.time() - start_time

    return {
        "text": response.text,
        "elapsed_seconds": round(elapsed, 2),
        "file": str(audio_file)
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    audio_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "en"

    try:
        result = transcribe(audio_path, language)

        print(f"\nResultaat:")
        print(f"{'=' * 40}")
        print(result["text"])
        print(f"{'=' * 40}")
        print(f"\nLatency: {result['elapsed_seconds']}s")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error bij transcriptie: {e}")
        print("\nIs de Voxtral container gestart?")
        print("Run: docker compose up -d")
        sys.exit(1)


if __name__ == "__main__":
    main()
