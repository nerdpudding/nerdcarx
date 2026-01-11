#!/usr/bin/env python3
"""
VAD Listener - Voice Activity Detection voor Voxtral STT
Luistert naar microfoon, detecteert spraak, stuurt naar Voxtral.

Gebruik:
    conda activate nerdcarx-vad
    python vad_listen.py              # Transcriptie mode
    python vad_listen.py --chat       # Chat mode (Voxtral beantwoordt)
"""

import argparse
import io
import sys
import wave
from collections import deque

import numpy as np
import pyaudio
import requests
import torch
from silero_vad import load_silero_vad

# Configuratie
SAMPLE_RATE = 16000  # Silero VAD vereist 16kHz
CHUNK_SAMPLES = 512  # ~32ms @ 16kHz
CHANNELS = 1
FORMAT = pyaudio.paInt16

# VAD parameters
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5  # seconden stilte voor einde detectie
MIN_SPEECH_DURATION = 0.3  # minimale spraak duur in seconden
PRE_SPEECH_BUFFER = 0.3  # seconden audio voor spraak start bewaren

# Voxtral endpoint
VOXTRAL_URL = "http://localhost:8150"


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
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    return buffer.getvalue()


def send_to_voxtral(audio_bytes: bytes, chat_mode: bool = False, system_prompt: str = None) -> str:
    """Stuur audio naar Voxtral en krijg response."""
    if chat_mode:
        # Chat mode: Voxtral beantwoordt de vraag
        import base64
        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')

        prompt = system_prompt or "Je bent een behulpzame AI assistent. Beantwoord de vraag van de gebruiker kort en duidelijk in het Nederlands."

        payload = {
            "model": "mistralai/Voxtral-Mini-3B-2507",
            "temperature": 0.2,
            "top_p": 0.95,
            "max_tokens": 500,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "audio_url", "audio_url": {"url": f"data:audio/wav;base64,{b64_audio}"}}
                ]}
            ]
        }

        response = requests.post(
            f"{VOXTRAL_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    else:
        # Transcriptie mode
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


def main():
    parser = argparse.ArgumentParser(description='VAD Listener voor Voxtral')
    parser.add_argument('--chat', action='store_true', help='Chat mode: Voxtral beantwoordt vragen')
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

    # Bereken chunks voor timing
    chunks_per_second = SAMPLE_RATE / CHUNK_SAMPLES
    silence_chunks = int(args.silence_duration * chunks_per_second)
    min_speech_chunks = int(MIN_SPEECH_DURATION * chunks_per_second)
    pre_buffer_chunks = int(PRE_SPEECH_BUFFER * chunks_per_second)

    mode_str = "CHAT" if args.chat else "TRANSCRIPTIE"
    print(f"\n🎙️ VAD Listener gestart ({mode_str} mode)")
    print("=" * 60)
    print("Instructies:")
    print("  • Spreek wanneer je klaar bent - VAD detecteert automatisch")
    print(f"  • Stilte van {args.silence_duration}s beëindigt opname")
    print("  • Ctrl+C om te stoppen")
    print("=" * 60)

    # Pre-speech buffer (ring buffer)
    pre_buffer = deque(maxlen=pre_buffer_chunks)

    try:
        while True:
            print("\n🎧 Luisteren... (spreek wanneer klaar)")

            # Reset state
            is_speaking = False
            speech_chunks = 0
            silence_count = 0
            audio_buffer = []

            # Reset VAD state
            vad_model.reset_states()

            while True:
                # Lees audio chunk
                audio_chunk = stream.read(CHUNK_SAMPLES, exception_on_overflow=False)
                audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                audio_tensor = torch.from_numpy(audio_np)

                # VAD inference
                speech_prob = vad_model(audio_tensor, SAMPLE_RATE).item()

                if speech_prob > VAD_THRESHOLD:
                    if not is_speaking:
                        print("🔴 Spraak gedetecteerd - opname gestart")
                        is_speaking = True
                        # Voeg pre-buffer toe aan audio
                        audio_buffer = list(pre_buffer)

                    audio_buffer.append(audio_chunk)
                    speech_chunks += 1
                    silence_count = 0
                else:
                    if is_speaking:
                        audio_buffer.append(audio_chunk)
                        silence_count += 1

                        if silence_count >= silence_chunks:
                            # Einde spraak gedetecteerd
                            print("⏸️ Stilte gedetecteerd - opname gestopt")

                            # Check minimale spraak duur
                            if speech_chunks >= min_speech_chunks:
                                break
                            else:
                                print("⚠️ Te kort, negeren...")
                                is_speaking = False
                                speech_chunks = 0
                                silence_count = 0
                                audio_buffer = []
                    else:
                        # Niet aan het spreken, vul pre-buffer
                        pre_buffer.append(audio_chunk)

            # Verwerk opgenomen audio
            if audio_buffer:
                audio_data = np.frombuffer(b''.join(audio_buffer), dtype=np.int16)
                duration = len(audio_data) / SAMPLE_RATE
                print(f"📊 Opname: {duration:.1f}s")

                # Converteer naar WAV
                wav_bytes = audio_to_wav_bytes(audio_data, SAMPLE_RATE)

                # Stuur naar Voxtral
                print("📤 Verzenden naar Voxtral...")
                try:
                    result = send_to_voxtral(wav_bytes, chat_mode=args.chat)

                    if args.chat:
                        print(f"🤖 Antwoord: {result}")
                    else:
                        print(f"📝 Transcriptie: {result}")

                except requests.exceptions.ConnectionError:
                    print("❌ Kan niet verbinden met Voxtral. Draait de container?")
                except requests.exceptions.Timeout:
                    print("❌ Timeout bij Voxtral request")
                except Exception as e:
                    print(f"❌ Fout: {e}")

    except KeyboardInterrupt:
        print("\n\n👋 VAD Listener gestopt.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    main()
