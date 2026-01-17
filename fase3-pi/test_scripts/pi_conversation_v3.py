#!/usr/bin/env python3
"""
Pi Conversation v3 - Simpele client, debug op orchestrator

Dit script is een vereenvoudigde versie van v2:
- Geen timing weergave (timing staat nu in orchestrator logs)
- Alleen lokale events: wake word, VAD, function execution, audio playback
- Cleaner output

Flow:
    [Start] -> [Wake word] -> [VAD Loop: luisteren -> opnemen -> verwerken -> afspelen]

Debug info (timing STT/LLM/TTS) wordt getoond via:
    docker compose logs orchestrator -f

Gebruik op Pi:
    conda activate nerdcarx
    cd ~/fase3-pi/test_scripts
    python pi_conversation_v3.py
"""

import asyncio
import base64
import io
import json
import os
import signal
import subprocess
import sys
import termios
import time
import wave
from collections import deque
from pathlib import Path

import numpy as np
import pyaudio
import onnxruntime as ort
from openwakeword.model import Model as WakeWordModel

# Global flag voor clean shutdown
_shutdown_requested = False


def _signal_handler(signum, frame):
    """Handle Ctrl+C."""
    global _shutdown_requested
    _shutdown_requested = True
    print("\n\n👋 Interrupt received, stopping...")
    # Raise om uit blocking calls te komen
    raise KeyboardInterrupt()

# ============================================================================
# CONFIGURATIE
# ============================================================================

# Network
DESKTOP_IP = "192.168.1.161"
WEBSOCKET_URL = f"ws://{DESKTOP_IP}:8200/ws"

# Audio hardware (Pi specifiek)
MIC_DEVICE_NAME = "USB PnP Sound Device"
SPEAKER_DEVICE_NAME = "hifiberry"
SPEAKER_GPIO = 20

# Device indices (auto-gedetecteerd)
MIC_DEVICE_INDEX = None
MIC_SAMPLE_RATE = None
SPEAKER_DEVICE_INDEX = None
SPEAKER_SAMPLE_RATE = None

# Audio parameters
MODEL_SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Wake word
WAKE_WORD = "hey_jarvis"
WAKE_THRESHOLD = 0.5
WAKE_CHUNK_MS = 80

# VAD parameters
VAD_CHUNK_MS = 30
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5
MIN_SPEECH_DURATION = 0.3
PRE_SPEECH_BUFFER = 0.3

# Audio gain
AUDIO_GAIN = 10.0

# Silero VAD
VAD_MODEL_URL = "https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.onnx"
VAD_MODEL_PATH = os.path.expanduser("~/silero_vad_v4.onnx")

# Mock photo
MOCK_PHOTO_PATH = Path(__file__).parent / "mock_photo.jpg"

# Emotie emoji's
EMOTION_EMOJIS = {
    "happy": "😊", "sad": "😢", "angry": "😠",
    "surprised": "😲", "neutral": "😐", "curious": "🤔",
    "confused": "😕", "excited": "🤩", "thinking": "💭",
    "shy": "😳", "love": "😍", "tired": "😴",
    "bored": "😑", "proud": "😤", "worried": "😟"
}


# ============================================================================
# SILERO VAD
# ============================================================================

class SileroVAD:
    """Silero VAD v4 via ONNX Runtime."""

    def __init__(self):
        if not os.path.exists(VAD_MODEL_PATH):
            print("📥 Downloading Silero VAD v4...")
            import urllib.request
            urllib.request.urlretrieve(VAD_MODEL_URL, VAD_MODEL_PATH)

        sess_options = ort.SessionOptions()
        sess_options.inter_op_num_threads = 1
        sess_options.intra_op_num_threads = 1
        self.session = ort.InferenceSession(
            VAD_MODEL_PATH,
            sess_options=sess_options,
            providers=["CPUExecutionProvider"]
        )
        self.reset_state()

    def reset_state(self):
        self.h = np.zeros((2, 1, 64), dtype=np.float32)
        self.c = np.zeros((2, 1, 64), dtype=np.float32)
        self.sr = np.array(MODEL_SAMPLE_RATE, dtype=np.int64)

    def process(self, audio_chunk: np.ndarray) -> float:
        audio = (audio_chunk / 32767.0).astype(np.float32).reshape(1, -1)
        out, self.h, self.c = self.session.run(None, {
            'input': audio, 'h': self.h, 'c': self.c, 'sr': self.sr
        })
        return out[0][0]


# ============================================================================
# AUDIO HELPERS
# ============================================================================

def enable_speaker():
    """Activeer speaker amplifier via GPIO."""
    try:
        subprocess.run(["pinctrl", "set", str(SPEAKER_GPIO), "op", "dh"],
                      check=True, capture_output=True)
    except Exception:
        pass


def play_beep(p: pyaudio.PyAudio, freq: int = 880, duration: float = 0.15) -> None:
    """Play a short beep sound."""
    try:
        sample_rate = SPEAKER_SAMPLE_RATE or 44100
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        # Sine wave with fade in/out
        wave = np.sin(2 * np.pi * freq * t)
        fade_samples = int(sample_rate * 0.02)
        wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        audio = (wave * 16000).astype(np.int16)

        stream = p.open(format=FORMAT, channels=1, rate=sample_rate,
                       output=True, output_device_index=SPEAKER_DEVICE_INDEX)
        stream.write(audio.tobytes())
        stream.stop_stream()
        stream.close()
    except Exception:
        pass


def play_startup_sound(p: pyaudio.PyAudio) -> None:
    """Play R2D2-like startup sequence."""
    # Quick ascending beeps
    play_beep(p, freq=400, duration=0.08)
    time.sleep(0.02)
    play_beep(p, freq=600, duration=0.06)
    time.sleep(0.02)
    play_beep(p, freq=800, duration=0.1)
    time.sleep(0.05)
    play_beep(p, freq=1000, duration=0.15)


def apply_gain(audio: np.ndarray, gain: float = AUDIO_GAIN) -> np.ndarray:
    amplified = audio.astype(np.float32) * gain
    return np.clip(amplified, -32768, 32767).astype(np.int16)


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int = MODEL_SAMPLE_RATE) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return buffer.getvalue()


def play_audio_base64(audio_base64: str, p: pyaudio.PyAudio) -> None:
    """Play base64 encoded WAV audio."""
    try:
        audio_bytes = base64.b64decode(audio_base64)
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=SPEAKER_DEVICE_INDEX
            )
            stream.write(wf.readframes(wf.getnframes()))
            stream.stop_stream()
            stream.close()
    except Exception as e:
        print(f"  ⚠️ Audio error: {e}")


def resample_audio(audio: np.ndarray, orig_rate: int, target_rate: int) -> np.ndarray:
    if orig_rate == target_rate:
        return audio
    duration = len(audio) / orig_rate
    new_length = int(duration * target_rate)
    old_indices = np.linspace(0, len(audio) - 1, new_length)
    return np.interp(old_indices, np.arange(len(audio)), audio.astype(np.float32)).astype(np.int16)


def find_device_by_name(p: pyaudio.PyAudio, name_pattern: str, need_input: bool = False, need_output: bool = False):
    name_lower = name_pattern.lower()
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if name_lower in info.get('name', '').lower():
                if need_input and info.get('maxInputChannels', 0) == 0:
                    continue
                if need_output and info.get('maxOutputChannels', 0) == 0:
                    continue
                return (i, int(info.get('defaultSampleRate', 44100)), info.get('name', ''))
        except Exception:
            continue
    return (-1, 0, "")


# ============================================================================
# REMOTE TOOL HANDLERS
# ============================================================================

def execute_take_photo() -> tuple[str, str]:
    """Execute take_photo - lees mock foto."""
    if MOCK_PHOTO_PATH.exists():
        print("  📷 Reading mock_photo.jpg")
        with open(MOCK_PHOTO_PATH, "rb") as f:
            return "Photo captured", base64.b64encode(f.read()).decode('utf-8')
    return "No camera available", ""


async def handle_function_request(ws, payload: dict, conv_id: str) -> tuple[bool, str]:
    """
    Handle FUNCTION_REQUEST from orchestrator.

    Returns:
        (should_sleep, result_text)
    """
    name = payload.get("name", "")
    args = payload.get("arguments", {})
    request_id = payload.get("request_id", "")

    print(f"  🔧 [{name}] {args}")

    result_text, image_base64 = "", ""
    should_sleep = False

    if name == "take_photo":
        result_text, image_base64 = execute_take_photo()
    elif name == "show_emotion":
        emotion = args.get("emotion", "neutral")
        emoji = EMOTION_EMOJIS.get(emotion, "🤖")
        print(f"  {emoji} Emotion: {emotion}")
        result_text = f"Showing {emotion}"
    elif name == "go_to_sleep":
        print("  💤 Going to sleep...")
        result_text = "Going to sleep"
        should_sleep = True
    else:
        result_text = f"Unknown tool: {name}"

    # Send result back
    msg = {
        "type": "function_result",
        "conversation_id": conv_id,
        "timestamp": time.time(),
        "payload": {"name": name, "request_id": request_id, "result": result_text}
    }
    if image_base64:
        msg["payload"]["image_base64"] = image_base64

    await ws.send(json.dumps(msg))
    return should_sleep, result_text


# ============================================================================
# WEBSOCKET CLIENT
# ============================================================================

async def send_audio_and_receive(audio_bytes: bytes, conv_id: str) -> dict:
    """Send audio, receive response."""
    import websockets

    result = {"text": "", "chunks": [], "emotion": "neutral", "should_sleep": False}

    try:
        async with websockets.connect(f"{WEBSOCKET_URL}?conversation_id={conv_id}", ping_timeout=30) as ws:
            # Send audio
            msg = {
                "type": "audio_process",
                "conversation_id": conv_id,
                "timestamp": time.time(),
                "payload": {"audio_base64": base64.b64encode(audio_bytes).decode(), "language": "nl"}
            }
            await ws.send(json.dumps(msg))

            # Receive responses
            while True:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=60.0)
                    data = json.loads(raw)
                    msg_type = data.get("type", "")

                    if msg_type == "response":
                        payload = data.get("payload", {})
                        result["text"] = payload.get("text", "")
                        emotion = payload.get("emotion", "neutral")
                        if isinstance(emotion, dict):
                            emotion = emotion.get("current", "neutral")
                        result["emotion"] = emotion

                    elif msg_type == "audio_chunk":
                        payload = data.get("payload", {})
                        result["chunks"].append(payload.get("audio_base64"))
                        if payload.get("is_last"):
                            break

                    elif msg_type == "function_request":
                        should_sleep, _ = await handle_function_request(ws, data.get("payload", {}), conv_id)
                        if should_sleep:
                            result["should_sleep"] = True

                    elif msg_type == "error":
                        print(f"  ❌ {data.get('payload', {}).get('error', 'Error')}")
                        break

                except asyncio.TimeoutError:
                    print("  ⚠️ Timeout")
                    break

    except Exception as e:
        print(f"  ❌ Connection error: {e}")

    return result


# ============================================================================
# CONVERSATION
# ============================================================================

def wait_for_wake_word(p: pyaudio.PyAudio, wake_model) -> bool:
    """Wait for wake word."""
    global _shutdown_requested
    chunk_size = int(MIC_SAMPLE_RATE * WAKE_CHUNK_MS / 1000)
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=MIC_SAMPLE_RATE,
                    input=True, input_device_index=MIC_DEVICE_INDEX, frames_per_buffer=chunk_size)

    print("\n🎧 Waiting for wake word... (say 'hey jarvis')")

    try:
        while not _shutdown_requested:
            # Non-blocking read
            available = stream.get_read_available()
            if available < chunk_size:
                time.sleep(0.01)
                continue

            data = stream.read(chunk_size, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16)
            if MIC_SAMPLE_RATE != MODEL_SAMPLE_RATE:
                audio = resample_audio(audio, MIC_SAMPLE_RATE, MODEL_SAMPLE_RATE)

            score = wake_model.predict(audio).get(WAKE_WORD, 0)
            if score > WAKE_THRESHOLD:
                print(f"✨ Wake word detected! (score: {score:.2f})")
                stream.stop_stream()
                stream.close()
                play_beep(p)  # Confirmation beep
                return True
        return False  # Shutdown requested
    except Exception as e:
        print(f"❌ Wake word error: {e}")
        stream.stop_stream()
        stream.close()
        return False


def record_speech(stream, vad: SileroVAD, pre_buffer: deque, chunk_size: int) -> tuple:
    """Record speech using VAD."""
    global _shutdown_requested
    vad.reset_state()
    chunks_per_second = MIC_SAMPLE_RATE / chunk_size
    silence_chunks = int(SILENCE_DURATION * chunks_per_second)
    min_speech_chunks = int(MIN_SPEECH_DURATION * chunks_per_second)

    is_speaking = False
    speech_chunks = 0
    silence_count = 0
    audio_buffer = []

    while not _shutdown_requested:
        # Non-blocking read: wacht max 100ms op data
        available = stream.get_read_available()
        if available < chunk_size:
            time.sleep(0.01)  # 10ms wait
            continue

        data = stream.read(chunk_size, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        vad_chunk = resample_audio(audio, MIC_SAMPLE_RATE, MODEL_SAMPLE_RATE) if MIC_SAMPLE_RATE != MODEL_SAMPLE_RATE else audio

        if vad.process(vad_chunk) > VAD_THRESHOLD:
            if not is_speaking:
                print("  🔴 Speech detected")
                is_speaking = True
                audio_buffer = list(pre_buffer)
            audio_buffer.append(data)
            speech_chunks += 1
            silence_count = 0
        else:
            if is_speaking:
                audio_buffer.append(data)
                silence_count += 1
                if silence_count >= silence_chunks:
                    if speech_chunks >= min_speech_chunks:
                        break
                    is_speaking = False
                    speech_chunks = 0
                    audio_buffer = []
            else:
                pre_buffer.append(data)

    if _shutdown_requested:
        return np.array([], dtype=np.int16), 0.0

    all_audio = np.frombuffer(b''.join(audio_buffer), dtype=np.int16)
    return all_audio, len(all_audio) / MIC_SAMPLE_RATE


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Signal handler voor Ctrl+C
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Terminal settings
    old_term = termios.tcgetattr(sys.stdin) if sys.stdin.isatty() else None

    print("=" * 50)
    print("🤖 Pi Conversation v3")
    print(f"   Desktop: {DESKTOP_IP}")
    print(f"   Debug: docker compose logs orchestrator -f")
    print("=" * 50)

    enable_speaker()

    # Load models
    print("Loading models...")
    wake_model = WakeWordModel()
    vad = SileroVAD()

    # Audio setup
    p = pyaudio.PyAudio()

    global MIC_DEVICE_INDEX, MIC_SAMPLE_RATE, SPEAKER_DEVICE_INDEX, SPEAKER_SAMPLE_RATE
    MIC_DEVICE_INDEX, MIC_SAMPLE_RATE, _ = find_device_by_name(p, MIC_DEVICE_NAME, need_input=True)
    SPEAKER_DEVICE_INDEX, SPEAKER_SAMPLE_RATE, _ = find_device_by_name(p, SPEAKER_DEVICE_NAME, need_output=True)

    if MIC_DEVICE_INDEX < 0:
        print("❌ Mic not found")
        return
    if SPEAKER_DEVICE_INDEX < 0:
        print("❌ Speaker not found")
        return

    print(f"✅ Mic: {MIC_SAMPLE_RATE}Hz, Speaker: {SPEAKER_SAMPLE_RATE}Hz")

    # Startup sound
    play_startup_sound(p)

    # Wait for wake word
    if not wait_for_wake_word(p, wake_model):
        return

    # Start conversation
    conv_id = f"pi-{int(time.time())}"
    turn = 0
    chunk_size = int(MIC_SAMPLE_RATE * VAD_CHUNK_MS / 1000)
    pre_buffer = deque(maxlen=int(PRE_SPEECH_BUFFER * MIC_SAMPLE_RATE / chunk_size))

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=MIC_SAMPLE_RATE,
                    input=True, input_device_index=MIC_DEVICE_INDEX, frames_per_buffer=chunk_size)

    print("\n🎙️ Conversation started! (no wake word needed)")

    try:
        # Conversation loop
        while not _shutdown_requested:
            turn += 1
            print(f"\n[Turn {turn}]")
            print("  🎧 Listening...")

            # Record
            audio, duration = record_speech(stream, vad, pre_buffer, chunk_size)

            # Check for shutdown or empty audio
            if _shutdown_requested or len(audio) == 0:
                break

            print(f"  ✅ Recorded ({duration:.1f}s)")

            # Process
            audio = apply_gain(audio)
            if MIC_SAMPLE_RATE != MODEL_SAMPLE_RATE:
                audio = resample_audio(audio, MIC_SAMPLE_RATE, MODEL_SAMPLE_RATE)

            print("  📡 Sending...")
            result = asyncio.run(send_audio_and_receive(audio_to_wav_bytes(audio), conv_id))

            # Show response
            if result["text"]:
                emoji = EMOTION_EMOJIS.get(result["emotion"], "🤖")
                print(f"  {emoji} {result['text'][:80]}...")

            # Play audio
            if result["chunks"]:
                print(f"  🔊 Playing ({len(result['chunks'])} chunks)")
                for chunk in result["chunks"]:
                    if chunk:
                        play_audio_base64(chunk, p)

            # Check for sleep command - restart script for clean state
            if result.get("should_sleep"):
                print("\n😴 Going to sleep (restarting in 2s...)")
                play_beep(p, freq=660, duration=0.1)
                time.sleep(0.05)
                play_beep(p, freq=440, duration=0.15)
                # Cleanup
                stream.stop_stream()
                stream.close()
                p.terminate()
                if old_term is not None:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term)
                time.sleep(2)
                # Restart script
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return  # Never reached

            pre_buffer.clear()

    except KeyboardInterrupt:
        print("\n\n👋 Stopped")

    finally:
        # Cleanup audio - met try/except om te zorgen dat termios altijd hersteld wordt
        if stream:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
        try:
            p.terminate()
        except Exception:
            pass

        # Terminal settings ALTIJD herstellen (voorkomt dat keyboard niet werkt)
        if old_term is not None:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term)
            except Exception:
                pass

        print("Cleanup done.")


if __name__ == "__main__":
    main()
