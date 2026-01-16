#!/usr/bin/env python3
"""
Test Voxtral audio understanding (Q&A over audio).

Dit demonstreert dat Voxtral meer kan dan alleen transcriptie:
je kunt vragen stellen over de audio content.

Gebruik:
    python3 test_audio_qa.py <audio_file> "<vraag>"

Voorbeelden:
    python3 test_audio_qa.py obama.mp3 "What is this person talking about?"
    python3 test_audio_qa.py interview.wav "Wat is de stemming van de spreker?"
    python3 test_audio_qa.py meeting.mp3 "Summarize the main points discussed."
"""

import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
    from mistral_common.protocol.instruct.messages import TextChunk, AudioChunk, UserMessage
    from mistral_common.audio import Audio
except ImportError as e:
    print(f"Error: ontbrekende package: {e}")
    print("Run: pip install openai mistral_common")
    sys.exit(1)


def audio_qa(audio_path: str, question: str) -> dict:
    """Stel een vraag over audio content via Voxtral."""

    client = OpenAI(
        base_url="http://localhost:8150/v1",
        api_key="dummy"
    )

    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio bestand niet gevonden: {audio_path}")

    print(f"Audio: {audio_file.name}")
    print(f"Vraag: {question}")
    print("-" * 40)

    # Laad audio en maak chunks
    audio = Audio.from_file(str(audio_file), strict=False)
    audio_chunk = AudioChunk.from_audio(audio)
    text_chunk = TextChunk(text=question)

    # Maak user message in OpenAI formaat
    user_msg = UserMessage(content=[audio_chunk, text_chunk]).to_openai()

    start_time = time.time()

    response = client.chat.completions.create(
        model="RedHatAI/Voxtral-Mini-3B-2507-FP8-dynamic",
        messages=[user_msg],
        temperature=0.2,
        top_p=0.95,
    )

    elapsed = time.time() - start_time
    answer = response.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
        "elapsed_seconds": round(elapsed, 2),
        "file": str(audio_file)
    }


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    audio_path = sys.argv[1]
    question = sys.argv[2]

    try:
        result = audio_qa(audio_path, question)

        print(f"\nAntwoord:")
        print(f"{'=' * 40}")
        print(result["answer"])
        print(f"{'=' * 40}")
        print(f"\nLatency: {result['elapsed_seconds']}s")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        print("\nIs de Voxtral container gestart?")
        print("Run: docker compose up -d")
        sys.exit(1)


if __name__ == "__main__":
    main()
