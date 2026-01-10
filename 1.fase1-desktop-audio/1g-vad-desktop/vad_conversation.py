#!/usr/bin/env python3
"""
VAD Conversation - Voice Conversation met Voxtral
Hands-free heen-en-weer gesprek met conversation history.

Gebruik:
    conda activate nerdcarx-vad
    python vad_conversation.py
    python vad_conversation.py --system-prompt "Je bent een grappige robot."
"""

import argparse
import io
import sys
import wave
from collections import deque
from datetime import datetime

import numpy as np
import pyaudio
import requests
import torch
from silero_vad import load_silero_vad

# Configuratie
SAMPLE_RATE = 16000
CHUNK_SAMPLES = 512
CHANNELS = 1
FORMAT = pyaudio.paInt16

# VAD parameters
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5
MIN_SPEECH_DURATION = 0.3
PRE_SPEECH_BUFFER = 0.3

# Voxtral endpoint
VOXTRAL_URL = "http://localhost:8150"

# Stop commando (expliciet - moet exact dit zeggen)
STOP_PHRASE = "stop nu het gesprek"

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """Je bent een behulpzame en vriendelijke AI assistent.
Beantwoord vragen kort en duidelijk in het Nederlands.
Wees conversationeel en natuurlijk."""


def list_audio_devices():
    """Toon beschikbare audio input devices."""
    p = pyaudio.PyAudio()
    print("\n🎤 Beschikbare Audio Input Devices:")
    print("=" * 60)

    default_index = p.get_default_input_device_info()['index']
    devices = []

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            default_marker = " (DEFAULT)" if i == default_index else ""
            print(f"   {i}: {info['name']}{default_marker}")
            devices.append(i)

    print("=" * 60)
    p.terminate()
    return devices, default_index


def select_device():
    """Laat gebruiker audio device selecteren."""
    devices, default_index = list_audio_devices()

    try:
        choice = input(f"Selecteer device ID (default: {default_index}): ").strip()
        if choice == "":
            return default_index
        device_id = int(choice)
        if device_id not in devices:
            print(f"⚠️  Device {device_id} niet gevonden, gebruik default.")
            return default_index
        return device_id
    except (ValueError, KeyboardInterrupt):
        return default_index


def audio_to_wav_bytes(audio_data: np.ndarray, sample_rate: int) -> bytes:
    """Converteer numpy audio array naar WAV bytes."""
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    return buffer.getvalue()


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribeer audio via Voxtral."""
    files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
    data = {'model': 'mistralai/Voxtral-Mini-3B-2507'}

    response = requests.post(
        f"{VOXTRAL_URL}/v1/audio/transcriptions",
        files=files,
        data=data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()['text']


def chat_with_history(conversation_history: list, system_prompt: str) -> str:
    """Stuur conversation history naar Voxtral en krijg antwoord."""
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)

    payload = {
        "model": "mistralai/Voxtral-Mini-3B-2507",
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 500,
        "messages": messages
    }

    response = requests.post(
        f"{VOXTRAL_URL}/v1/chat/completions",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


def is_stop_command(text: str) -> bool:
    """Check of de tekst het stop commando bevat."""
    return STOP_PHRASE in text.lower()


def record_speech(stream, vad_model, silence_chunks, min_speech_chunks, pre_buffer):
    """Neem spraak op met VAD detectie."""
    is_speaking = False
    speech_chunks = 0
    silence_count = 0
    audio_buffer = []

    vad_model.reset_states()

    while True:
        audio_chunk = stream.read(CHUNK_SAMPLES, exception_on_overflow=False)
        audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_np)

        speech_prob = vad_model(audio_tensor, SAMPLE_RATE).item()

        if speech_prob > VAD_THRESHOLD:
            if not is_speaking:
                print("🔴 Spraak gedetecteerd...")
                is_speaking = True
                audio_buffer = list(pre_buffer)

            audio_buffer.append(audio_chunk)
            speech_chunks += 1
            silence_count = 0
        else:
            if is_speaking:
                audio_buffer.append(audio_chunk)
                silence_count += 1

                if silence_count >= silence_chunks:
                    if speech_chunks >= min_speech_chunks:
                        return audio_buffer
                    else:
                        is_speaking = False
                        speech_chunks = 0
                        silence_count = 0
                        audio_buffer = []
            else:
                pre_buffer.append(audio_chunk)


def main():
    parser = argparse.ArgumentParser(description='VAD Conversation met Voxtral')
    parser.add_argument('--system-prompt', type=str, default=DEFAULT_SYSTEM_PROMPT,
                        help='Custom system prompt voor de AI')
    parser.add_argument('--silence-duration', type=float, default=SILENCE_DURATION,
                        help=f'Stilte duur voor einde detectie (default: {SILENCE_DURATION}s)')
    parser.add_argument('--device', type=int, help='Audio device ID (skip selectie)')
    args = parser.parse_args()

    # Laad VAD model
    print("🔄 VAD model laden...")
    vad_model = load_silero_vad()
    print("✅ VAD model geladen")

    # Selecteer audio device
    if args.device is not None:
        device_id = args.device
    else:
        device_id = select_device()

    # PyAudio setup
    p = pyaudio.PyAudio()
    device_info = p.get_device_info_by_index(device_id)
    print(f"✅ Geselecteerd: {device_info['name']}")

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=device_id,
        frames_per_buffer=CHUNK_SAMPLES
    )

    # Timing berekeningen
    chunks_per_second = SAMPLE_RATE / CHUNK_SAMPLES
    silence_chunks = int(args.silence_duration * chunks_per_second)
    min_speech_chunks = int(MIN_SPEECH_DURATION * chunks_per_second)
    pre_buffer_chunks = int(PRE_SPEECH_BUFFER * chunks_per_second)
    pre_buffer = deque(maxlen=pre_buffer_chunks)

    # Conversation state
    conversation_history = []
    turn_count = 0

    print(f"\n🎙️ VAD Conversation gestart")
    print("=" * 60)
    print("Instructies:")
    print("  • Spreek wanneer je klaar bent")
    print(f"  • Stilte van {args.silence_duration}s beëindigt je beurt")
    print(f"  • Zeg '{STOP_PHRASE}' om te stoppen")
    print("  • Ctrl+C om direct te stoppen")
    print("=" * 60)

    try:
        while True:
            turn_count += 1
            print(f"\n[Turn {turn_count}]")
            print("🎧 Luisteren... (spreek wanneer klaar)")

            # Record speech
            audio_buffer = record_speech(
                stream, vad_model, silence_chunks,
                min_speech_chunks, pre_buffer
            )

            # Process audio
            audio_data = np.frombuffer(b''.join(audio_buffer), dtype=np.int16)
            duration = len(audio_data) / SAMPLE_RATE
            wav_bytes = audio_to_wav_bytes(audio_data, SAMPLE_RATE)

            # Transcribe
            print("📝 Transcriberen...")
            try:
                user_text = transcribe_audio(wav_bytes)
                print(f"👤 Jij: {user_text}")

                # Check stop command
                if is_stop_command(user_text):
                    print("\n👋 Stop commando gedetecteerd. Tot ziens!")
                    break

                # Add to history
                conversation_history.append({
                    "role": "user",
                    "content": user_text
                })

                # Get AI response
                print("🤔 Denken...")
                ai_response = chat_with_history(conversation_history, args.system_prompt)
                print(f"🤖 AI: {ai_response}")

                # Add response to history
                conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })

            except requests.exceptions.ConnectionError:
                print("❌ Kan niet verbinden met Voxtral. Draait de container?")
            except requests.exceptions.Timeout:
                print("❌ Timeout bij Voxtral request")
            except Exception as e:
                print(f"❌ Fout: {e}")

    except KeyboardInterrupt:
        print("\n\n👋 Conversation gestopt.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Print summary
        if conversation_history:
            print(f"\n📊 Samenvatting: {len(conversation_history) // 2} conversatie turns")


if __name__ == "__main__":
    main()
