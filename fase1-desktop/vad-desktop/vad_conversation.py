#!/usr/bin/env python3
"""
VAD Conversation - Voice Conversation via Orchestrator
Hands-free heen-en-weer gesprek met conversation history.

Flow: [Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral LLM] → response

Configuratie (prompts, model, etc.) staat centraal in: ../config.yml
De orchestrator regelt alles - deze client stuurt alleen tekst.

Gebruik:
    conda activate nerdcarx-vad
    python vad_conversation.py
"""

import argparse
import base64
import io
import sys
import time
import uuid
import wave
from collections import deque
from pathlib import Path

import numpy as np
import pyaudio
import requests
import torch
from silero_vad import load_silero_vad

# Audio response bestand (wordt elke keer overschreven)
RESPONSE_WAV = Path(__file__).parent / "last_response.wav"

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
TTS_URL = "http://localhost:8250"

# Stop commando (expliciet - moet exact dit zeggen)
STOP_PHRASE = "stop nu het gesprek"


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
    data = {
        'model': 'mistralai/Voxtral-Mini-3B-2507',
        'language': 'nl'  # Force Dutch transcription
    }

    response = requests.post(
        f"{VOXTRAL_URL}/v1/audio/transcriptions",
        files=files,
        data=data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()['text']


def chat_via_orchestrator(message: str, conversation_id: str) -> tuple:
    """
    Stuur bericht naar Orchestrator → Ministral LLM.
    Alle configuratie (prompt, model, etc.) wordt door de orchestrator geregeld.
    Returns: (response_text, function_calls, emotion_info, audio_base64)
    """
    payload = {
        "message": message,
        "conversation_id": conversation_id
    }

    response = requests.post(
        f"{ORCHESTRATOR_URL}/conversation",
        json=payload,
        timeout=120  # Langere timeout voor vision tool calls
    )
    response.raise_for_status()
    result = response.json()
    emotion_info = result.get('emotion', {"current": "neutral", "changed": False, "auto_reset": False})
    audio_base64 = result.get('audio_base64')
    timing_ms = result.get('timing_ms', {})
    return result['response'], result.get('function_calls', []), emotion_info, audio_base64, timing_ms


def play_audio(audio_base64: str) -> bool:
    """
    Speel audio af via speakers.
    Slaat audio op als last_response.wav (overschrijft vorige).
    Returns: True als afspelen gelukt is.
    """
    if not audio_base64:
        return False

    try:
        # Decode base64 naar WAV bytes
        audio_bytes = base64.b64decode(audio_base64)

        # Sla op als last_response.wav (overschrijft)
        RESPONSE_WAV.write_bytes(audio_bytes)

        # Lees WAV parameters
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

        # Speel af via PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(sample_width),
            channels=channels,
            rate=frame_rate,
            output=True
        )
        stream.write(frames)
        stream.stop_stream()
        stream.close()
        p.terminate()
        return True

    except Exception as e:
        print(f"⚠️ Audio playback fout: {e}")
        return False


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

    # Check TTS
    try:
        resp = requests.get(f"{TTS_URL}/health", timeout=5)
        results['tts'] = resp.status_code == 200
    except:
        results['tts'] = False

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

    if not services['tts']:
        print("⚠️ TTS niet bereikbaar op", TTS_URL)
        print("   Start met: conda activate nerdcarx-tts && uvicorn tts_service:app --port 8250")
        print("   (Gesprek werkt wel, maar zonder audio)")

    print("✅ Orchestrator en Voxtral bereikbaar")
    if services['tts']:
        print("✅ TTS bereikbaar (audio aan)")
    else:
        print("⚠️ TTS niet bereikbaar (audio uit)")

    # Herlaad orchestrator config en toon actieve configuratie
    try:
        requests.post(f"{ORCHESTRATOR_URL}/reload-config", timeout=5)
        config_resp = requests.get(f"{ORCHESTRATOR_URL}/config", timeout=5)
        if config_resp.ok:
            config = config_resp.json()
            print(f"📋 Config herladen:")
            print(f"   LLM: {config.get('ollama', {}).get('model', 'onbekend')}")
            print(f"   STT: {config.get('voxtral', {}).get('model', 'onbekend')}")
    except:
        print("⚠️ Kon config niet herladen (niet kritiek)")

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
    print("Flow: [Mic] → [VAD] → [STT] → [LLM] → [TTS] → [Speaker]")
    print(f"Conversation ID: {conversation_id}")
    print(f"TTS: {'🔊 Aan' if services['tts'] else '🔇 Uit'}")
    print("Vision: Via 'take_photo' tool (vraag: 'wat zie je?')")
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
            print(f"✅ Opgenomen ({duration:.1f}s)")

            # === TIMING START ===
            timings = {}

            # Transcribe via Voxtral
            print("📝 Transcriberen...", end="", flush=True)
            try:
                t_stt_start = time.perf_counter()
                user_text = transcribe_audio(wav_bytes)
                t_stt_end = time.perf_counter()
                timings['stt'] = (t_stt_end - t_stt_start) * 1000
                print(f" ✅ ({timings['stt']:.0f}ms)")
                print(f"👤 Jij: {user_text}")

                # Check stop command
                if is_stop_command(user_text):
                    print("\n👋 Stop commando gedetecteerd. Tot ziens!")
                    break

                # Get AI response via Orchestrator → Ministral + TTS
                print("🔄 Processing (LLM+TTS)...", end="", flush=True)
                t_proc_start = time.perf_counter()
                ai_response, function_calls, emotion_info, audio_base64, server_timing = chat_via_orchestrator(
                    user_text,
                    conversation_id
                )
                t_proc_end = time.perf_counter()
                timings['llm_tts_total'] = (t_proc_end - t_proc_start) * 1000
                timings['llm'] = server_timing.get('llm', 0)
                timings['tts'] = server_timing.get('tts', 0)
                print(f" ✅ (LLM: {timings['llm']}ms | TTS: {timings['tts']}ms)")

                # Emoji mapping voor emoties
                emotion_emojis = {
                    "happy": "😊", "sad": "😢", "angry": "😠",
                    "surprised": "😲", "neutral": "😐", "curious": "🤔",
                    "confused": "😕", "excited": "🤩", "thinking": "💭",
                    "shy": "😳", "love": "😍", "tired": "😴",
                    "bored": "😑", "proud": "😤", "worried": "😟"
                }

                # Debug: Toon ALLE tool calls
                if function_calls:
                    print(f"🔧 [TOOL CALLS] {len(function_calls)} tool call(s):")
                    for fc in function_calls:
                        name = fc.get('name', '')
                        args = fc.get('arguments', {})
                        print(f"   → {name}({args})")
                else:
                    print("🔧 [TOOL CALLS] geen")

                # Emotie status tonen
                emotion = emotion_info.get('current', 'neutral')
                emoji = emotion_emojis.get(emotion, "🤖")
                changed = emotion_info.get('changed', False)
                auto_reset = emotion_info.get('auto_reset', False)

                if auto_reset:
                    status = "auto-reset"
                elif changed:
                    status = "VERANDERD"
                else:
                    status = "behouden"

                print(f"🎭 [EMOTIE] {emotion} {emoji} ({status})")

                print(f"🤖 NerdCarX: {ai_response}")

                # Speel audio response af
                if audio_base64:
                    print("🔊 Afspelen...", end="", flush=True)
                    t_play_start = time.perf_counter()
                    if play_audio(audio_base64):
                        t_play_end = time.perf_counter()
                        timings['playback'] = (t_play_end - t_play_start) * 1000
                        print(f" ✅ ({timings['playback']:.0f}ms)")
                    else:
                        print(" ❌")
                        timings['playback'] = 0
                else:
                    print("⚠️ Geen audio ontvangen (TTS uit?)")
                    timings['playback'] = 0

                # === TIMING SUMMARY ===
                total = timings.get('stt', 0) + timings.get('llm_tts_total', 0) + timings.get('playback', 0)
                print(f"⏱️  [TIMING] STT: {timings.get('stt', 0):.0f}ms | LLM: {timings.get('llm', 0)}ms | TTS: {timings.get('tts', 0)}ms | Playback: {timings.get('playback', 0):.0f}ms | TOTAAL: {total:.0f}ms")

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
