#!/usr/bin/env python3
"""
VAD Conversation - Voice Conversation via Orchestrator
Hands-free heen-en-weer gesprek met conversation history.

Flow: [Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral LLM] → response

Gebruik:
    conda activate nerdcarx-vad
    python vad_conversation.py
    python vad_conversation.py --system-prompt "Je bent een grappige robot."
"""

import argparse
import io
import sys
import uuid
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

# Service endpoints
VOXTRAL_URL = "http://localhost:8150"
ORCHESTRATOR_URL = "http://localhost:8200"

# Stop commando (expliciet - moet exact dit zeggen)
STOP_PHRASE = "stop nu het gesprek"

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """Je bent NerdCarX, een vriendelijke en behulpzame robot assistent.
Je geeft korte, duidelijke antwoorden in het Nederlands.
Je bent nieuwsgierig en hebt een licht humoristische persoonlijkheid."""


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
    """Transcribeer audio via Voxtral STT."""
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


def chat_via_orchestrator(message: str, conversation_id: str, system_prompt: str = None) -> tuple:
    """
    Stuur bericht naar Orchestrator → Ministral LLM.
    Returns: (response_text, function_calls)
    """
    payload = {
        "message": message,
        "conversation_id": conversation_id
    }

    if system_prompt:
        payload["system_prompt"] = system_prompt

    response = requests.post(
        f"{ORCHESTRATOR_URL}/conversation",
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    result = response.json()
    return result['response'], result.get('function_calls', [])


def check_services() -> dict:
    """Check of alle services bereikbaar zijn."""
    results = {}

    # Check Orchestrator
    try:
        resp = requests.get(f"{ORCHESTRATOR_URL}/health", timeout=5)
        results['orchestrator'] = resp.status_code == 200
    except:
        results['orchestrator'] = False

    # Check Voxtral
    try:
        resp = requests.get(f"{VOXTRAL_URL}/health", timeout=5)
        results['voxtral'] = resp.status_code == 200
    except:
        results['voxtral'] = False

    return results


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
    parser = argparse.ArgumentParser(description='VAD Conversation via Orchestrator')
    parser.add_argument('--system-prompt', type=str, default=DEFAULT_SYSTEM_PROMPT,
                        help='Custom system prompt voor de AI')
    parser.add_argument('--silence-duration', type=float, default=SILENCE_DURATION,
                        help=f'Stilte duur voor einde detectie (default: {SILENCE_DURATION}s)')
    parser.add_argument('--device', type=int, help='Audio device ID (skip selectie)')
    args = parser.parse_args()

    # Check services
    print("🔄 Services checken...")
    services = check_services()

    if not services['orchestrator']:
        print("❌ Orchestrator niet bereikbaar op", ORCHESTRATOR_URL)
        print("   Start met: uvicorn main:app --port 8200")
        sys.exit(1)

    if not services['voxtral']:
        print("❌ Voxtral niet bereikbaar op", VOXTRAL_URL)
        print("   Start met: docker compose up -d")
        sys.exit(1)

    print("✅ Orchestrator en Voxtral bereikbaar")

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
    conversation_id = f"vad-{uuid.uuid4().hex[:8]}"
    turn_count = 0

    print(f"\n🎙️ VAD Conversation gestart")
    print("=" * 60)
    print("Flow: [Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral]")
    print(f"Conversation ID: {conversation_id}")
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

            # Transcribe via Voxtral
            print("📝 Transcriberen (Voxtral)...")
            try:
                user_text = transcribe_audio(wav_bytes)
                print(f"👤 Jij: {user_text}")

                # Check stop command
                if is_stop_command(user_text):
                    print("\n👋 Stop commando gedetecteerd. Tot ziens!")
                    break

                # Get AI response via Orchestrator → Ministral
                print("🤔 Denken (Ministral)...")
                ai_response, function_calls = chat_via_orchestrator(
                    user_text,
                    conversation_id,
                    args.system_prompt if turn_count == 1 else None  # System prompt alleen eerste keer
                )

                # Toon function calls (emoties)
                if function_calls:
                    for fc in function_calls:
                        if fc.get('name') == 'show_emotion':
                            emotion = fc.get('arguments', {}).get('emotion', 'neutral')
                            emotion_emojis = {
                                "happy": "😊", "sad": "😢", "angry": "😠",
                                "surprised": "😲", "neutral": "😐", "curious": "🤔",
                                "confused": "😕", "excited": "🤩", "thinking": "🧠"
                            }
                            emoji = emotion_emojis.get(emotion, "🤖")
                            print(f"🎭 [EMOTIE] {emotion} {emoji}")

                print(f"🤖 NerdCarX: {ai_response}")

            except requests.exceptions.ConnectionError as e:
                print(f"❌ Verbindingsfout: {e}")
            except requests.exceptions.Timeout:
                print("❌ Timeout bij request")
            except Exception as e:
                print(f"❌ Fout: {e}")

    except KeyboardInterrupt:
        print("\n\n👋 Conversation gestopt.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Cleanup conversation in orchestrator
        try:
            requests.delete(f"{ORCHESTRATOR_URL}/conversation/{conversation_id}", timeout=5)
        except:
            pass

        # Print summary
        print(f"\n📊 Samenvatting: {turn_count} turns")


if __name__ == "__main__":
    main()
