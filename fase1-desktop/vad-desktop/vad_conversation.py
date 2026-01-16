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
import json
import select
import sys
import termios
import threading
import time
import tty
import uuid
import wave
from collections import deque
from pathlib import Path

import numpy as np
import pyaudio
import requests
import torch
from silero_vad import load_silero_vad

# Global flag voor interrupt
playback_interrupted = False
playback_lock = threading.Lock()
original_terminal_settings = None  # Voor terminal restore na Ctrl+C

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
    Returns: (response_text, function_calls, emotion_info, audio_base64, timing_ms, normalized_text)
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
    normalized_text = result.get('normalized_text')
    return result['response'], result.get('function_calls', []), emotion_info, audio_base64, timing_ms, normalized_text


def chat_via_orchestrator_streaming(message: str, conversation_id: str, on_audio_chunk=None, on_metadata=None):
    """
    Streaming versie van chat_via_orchestrator.
    Roept callbacks aan zodra data binnenkomt:
    - on_metadata(metadata_dict): als LLM response + emotie info binnen is
    - on_audio_chunk(sentence, audio_base64, index): per zin audio

    Returns: (response_text, function_calls, emotion_info, timing_ms)
    """
    payload = {
        "message": message,
        "conversation_id": conversation_id
    }

    response_text = ""
    function_calls = []
    emotion_info = {"current": "neutral", "changed": False, "auto_reset": False}
    timing_ms = {}

    try:
        with requests.post(
            f"{ORCHESTRATOR_URL}/conversation/streaming",
            json=payload,
            stream=True,
            timeout=120
        ) as response:
            response.raise_for_status()

            event_type = None
            data_buffer = ""

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    # Lege regel = einde van event
                    if event_type and data_buffer:
                        try:
                            data = json.loads(data_buffer)

                            if event_type == "metadata":
                                response_text = data.get("response", "")
                                function_calls = data.get("function_calls", [])
                                emotion_info = data.get("emotion", emotion_info)
                                timing_ms = data.get("timing_ms", {})
                                if on_metadata:
                                    on_metadata(data)

                            elif event_type == "audio":
                                if on_audio_chunk:
                                    on_audio_chunk(
                                        data.get("sentence", ""),
                                        data.get("audio_base64"),
                                        data.get("index", 0),
                                        data.get("normalized")
                                    )

                            elif event_type == "error":
                                print(f"❌ Stream error: {data.get('error')}")

                        except json.JSONDecodeError:
                            pass

                    event_type = None
                    data_buffer = ""
                    continue

                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data_buffer = line[6:]

    except Exception as e:
        print(f"❌ Streaming error: {e}")

    return response_text, function_calls, emotion_info, timing_ms


def check_for_keypress():
    """Non-blocking check voor toetsaanslagen (Unix)."""
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def start_keyboard_listener():
    """Start keyboard listener in achtergrond thread."""
    global playback_interrupted, original_terminal_settings

    # Bewaar originele terminal settings VOORDAT we iets veranderen
    try:
        original_terminal_settings = termios.tcgetattr(sys.stdin)
    except:
        original_terminal_settings = None

    def listener():
        global playback_interrupted
        try:
            tty.setcbreak(sys.stdin.fileno())
            while True:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key == ' ':  # Spatiebalk
                        with playback_lock:
                            playback_interrupted = True
                        print("\n⏹️  Onderbroken!")
        except:
            pass

    thread = threading.Thread(target=listener, daemon=True)
    thread.start()
    return thread


def restore_terminal():
    """Herstel terminal settings (aanroepen bij exit)."""
    global original_terminal_settings
    if original_terminal_settings is not None:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_terminal_settings)
        except:
            pass


def reset_interrupt():
    """Reset interrupt flag."""
    global playback_interrupted
    with playback_lock:
        playback_interrupted = False


def is_interrupted():
    """Check of playback onderbroken moet worden."""
    global playback_interrupted
    with playback_lock:
        return playback_interrupted


def play_audio(audio_base64: str, check_interrupt: bool = False) -> bool:
    """
    Speel audio af via speakers.
    Slaat audio op als last_response.wav (overschrijft vorige).
    Als check_interrupt=True, check periodiek of playback onderbroken moet worden.
    Returns: True als afspelen gelukt is (niet onderbroken).
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
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)

        # Speel af via PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(sample_width),
            channels=channels,
            rate=frame_rate,
            output=True
        )

        if check_interrupt:
            # Speel in chunks en check voor interrupt
            chunk_size = frame_rate * sample_width * channels // 10  # 100ms chunks
            offset = 0
            interrupted = False

            while offset < len(frames):
                if is_interrupted():
                    interrupted = True
                    break

                chunk = frames[offset:offset + chunk_size]
                stream.write(chunk)
                offset += chunk_size

            stream.stop_stream()
            stream.close()
            p.terminate()
            return not interrupted
        else:
            # Normale playback (geen interrupt check)
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
    parser.add_argument('--streaming', action='store_true',
                        help='Forceer streaming mode (overschrijft config)')
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
    config_streaming = False
    try:
        requests.post(f"{ORCHESTRATOR_URL}/reload-config", timeout=5)
        config_resp = requests.get(f"{ORCHESTRATOR_URL}/config", timeout=5)
        if config_resp.ok:
            config = config_resp.json()
            print(f"📋 Config herladen:")
            print(f"   LLM: {config.get('ollama', {}).get('model', 'onbekend')}")
            print(f"   STT: {config.get('voxtral', {}).get('model', 'onbekend')}")
            config_streaming = config.get('tts', {}).get('streaming', False)
    except:
        print("⚠️ Kon config niet herladen (niet kritiek)")

    # Bepaal streaming mode: --streaming flag overschrijft config
    if args.streaming:
        use_streaming = True
    else:
        use_streaming = config_streaming

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

    # Start keyboard listener voor interrupt
    if use_streaming:
        start_keyboard_listener()

    print(f"\n🎙️ VAD Conversation gestart")
    print("=" * 60)
    if use_streaming:
        print("Flow: [Mic] → [VAD] → [STT] → [LLM] → [TTS per zin] → [Speaker]")
        print("Mode: 🚀 STREAMING (snellere response)")
    else:
        print("Flow: [Mic] → [VAD] → [STT] → [LLM] → [TTS] → [Speaker]")
        print("Mode: 📦 BATCH (alle TTS in één keer)")
    print(f"Conversation ID: {conversation_id}")
    print(f"TTS: {'🔊 Aan' if services['tts'] else '🔇 Uit'}")
    print("Vision: Via 'take_photo' tool (vraag: 'wat zie je?')")
    print("=" * 60)
    print("Instructies:")
    print("  • Spreek wanneer je klaar bent")
    print(f"  • Stilte van {args.silence_duration}s beëindigt je beurt")
    if use_streaming:
        print("  • Druk SPATIE om audio te onderbreken")
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

                # Emoji mapping voor emoties
                emotion_emojis = {
                    "happy": "😊", "sad": "😢", "angry": "😠",
                    "surprised": "😲", "neutral": "😐", "curious": "🤔",
                    "confused": "😕", "excited": "🤩", "thinking": "💭",
                    "shy": "😳", "love": "😍", "tired": "😴",
                    "bored": "😑", "proud": "😤", "worried": "😟"
                }

                if use_streaming:
                    # === STREAMING MODE ===
                    reset_interrupt()
                    print("🔄 Processing (LLM)...", end="", flush=True)
                    t_proc_start = time.perf_counter()

                    ai_response = ""
                    function_calls = []
                    emotion_info = {}
                    sentences_played = 0
                    was_interrupted = False
                    t_llm_done = None
                    t_last_tts_end = None
                    tts_times = []  # Per-zin TTS tijden
                    llm_ms = 0

                    def on_metadata(data):
                        nonlocal ai_response, function_calls, emotion_info, t_llm_done, t_last_tts_end, llm_ms
                        t_llm_done = time.perf_counter()
                        t_last_tts_end = t_llm_done  # Start punt voor eerste TTS meting
                        ai_response = data.get("response", "")
                        function_calls = data.get("function_calls", [])
                        emotion_info = data.get("emotion", {})
                        llm_ms = data.get("timing_ms", {}).get("llm", 0)
                        print(f" ✅ ({llm_ms}ms)")

                        # Toon tool calls
                        if function_calls:
                            print(f"🔧 [TOOL CALLS] {len(function_calls)} tool call(s):")
                            for fc in function_calls:
                                print(f"   → {fc.get('name', '')}({fc.get('arguments', {})})")
                        else:
                            print("🔧 [TOOL CALLS] geen")

                        # Emotie status
                        emotion = emotion_info.get('current', 'neutral')
                        emoji = emotion_emojis.get(emotion, "🤖")
                        changed = emotion_info.get('changed', False)
                        status = "VERANDERD" if changed else "behouden"
                        print(f"🎭 [EMOTIE] {emotion} {emoji} ({status})")
                        print(f"🤖 NerdCarX: {ai_response}")

                    def on_audio_chunk(sentence, audio_base64, index, normalized):
                        nonlocal sentences_played, was_interrupted, t_last_tts_end, tts_times
                        if was_interrupted or is_interrupted():
                            was_interrupted = True
                            return

                        # Meet TTS tijd (tijd sinds vorige chunk klaar was)
                        t_now = time.perf_counter()
                        tts_ms = (t_now - t_last_tts_end) * 1000
                        tts_times.append(tts_ms)

                        # Toon zin met TTS tijd
                        display_text = (normalized or sentence)[:40]
                        print(f"🔊 [{index+1}] \"{display_text}...\" (TTS: {tts_ms:.0f}ms)")

                        if audio_base64:
                            if not play_audio(audio_base64, check_interrupt=True):
                                was_interrupted = True
                            else:
                                sentences_played += 1
                            # Update t_last_tts_end NA playback voor volgende meting
                            t_last_tts_end = time.perf_counter()

                    chat_via_orchestrator_streaming(
                        user_text, conversation_id,
                        on_audio_chunk=on_audio_chunk,
                        on_metadata=on_metadata
                    )

                    t_proc_end = time.perf_counter()

                    if was_interrupted:
                        print(f"⏹️  Gestopt na {sentences_played} zin(nen)")

                    # === TIMING SUMMARY ===
                    total_tts = sum(tts_times)
                    total_turn = (t_proc_end - t_proc_start) * 1000
                    print(f"─" * 50)
                    print(f"⏱️  [TURN TIMING]")
                    print(f"    STT:  {timings.get('stt', 0):.0f}ms")
                    print(f"    LLM:  {llm_ms}ms")
                    print(f"    TTS:  {total_tts:.0f}ms ({len(tts_times)} zinnen: {', '.join(f'{t:.0f}' for t in tts_times)}ms)")
                    print(f"    ────────────────")
                    print(f"    TOTAAL: {timings.get('stt', 0) + llm_ms + total_tts:.0f}ms (excl. playback)")

                else:
                    # === BATCH MODE (origineel) ===
                    print("🔄 Processing (LLM+TTS)...", end="", flush=True)
                    t_proc_start = time.perf_counter()
                    ai_response, function_calls, emotion_info, audio_base64, server_timing, normalized_text = chat_via_orchestrator(
                        user_text,
                        conversation_id
                    )
                    t_proc_end = time.perf_counter()
                    timings['llm_tts_total'] = (t_proc_end - t_proc_start) * 1000
                    timings['llm'] = server_timing.get('llm', 0)
                    timings['tts'] = server_timing.get('tts', 0)
                    print(f" ✅ (LLM: {timings['llm']}ms | TTS: {timings['tts']}ms)")

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

                    # Toon genormaliseerde TTS tekst als die verschilt
                    if normalized_text:
                        print(f"📝 [TTS] {normalized_text}")

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
        # Herstel terminal settings (belangrijk voor keyboard listener)
        restore_terminal()

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
