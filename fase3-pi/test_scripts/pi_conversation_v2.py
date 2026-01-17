#!/usr/bin/env python3
"""
Pi Conversation v2 - Wake Word (eenmalig) + VAD Conversation Loop

Dit script combineert het beste van beide werelden:
- Wake word detectie ALLEEN bij start (niet per turn)
- Daarna VAD-based conversation loop zoals de desktop versie
- Uitgebreide debug output (timing, tool calls, emoties)
- Mock function call handling voor testing

Flow:
    [Start] -> [Wake word] -> [VAD Loop: luisteren -> opnemen -> verwerken -> afspelen]
                                    ^                                    |
                                    └────────────────────────────────────┘

Gebruik op Pi:
    conda activate nerdcarx
    cd ~/fase3-pi/test_scripts
    python pi_conversation_v2.py
"""

import asyncio
import base64
import io
import json
import os
import subprocess
import sys
import termios
import time
import wave
from collections import deque
from pathlib import Path

import numpy as np

# Note: PyAudio geeft veel ALSA/JACK warnings bij initialisatie.
# Deze zijn cosmetisch en niet kritiek - gewoon negeren.
# De warnings komen doordat PyAudio alle mogelijke audio configuraties probeert.
import pyaudio

import onnxruntime as ort
from openwakeword.model import Model as WakeWordModel

# ============================================================================
# CONFIGURATIE
# ============================================================================

# Network
DESKTOP_IP = "192.168.1.161"
WEBSOCKET_URL = f"ws://{DESKTOP_IP}:8200/ws"

# Audio hardware (Pi specifiek)
# Devices worden gezocht op naam, niet op index (indices kunnen veranderen na reboot)
MIC_DEVICE_NAME = "USB PnP Sound Device"  # USB mic
SPEAKER_DEVICE_NAME = "hifiberry"          # I2S speaker (mono, maar DAC is stereo)
SPEAKER_GPIO = 20                          # GPIO pin voor amplifier enable

# Device indices en sample rates (worden automatisch gedetecteerd bij startup)
MIC_DEVICE_INDEX = None
MIC_SAMPLE_RATE = None       # Native rate van mic (bijv. 44100Hz)
SPEAKER_DEVICE_INDEX = None
SPEAKER_SAMPLE_RATE = None   # Native rate van speaker

# Audio parameters
MODEL_SAMPLE_RATE = 16000    # Wat AI modellen verwachten (wake word, VAD, STT)
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Wake word (op MODEL_SAMPLE_RATE = 16kHz)
WAKE_WORD = "hey_jarvis"
WAKE_THRESHOLD = 0.5
WAKE_CHUNK_MS = 80           # 80ms chunks voor wake word

# VAD parameters (op MODEL_SAMPLE_RATE = 16kHz)
VAD_CHUNK_MS = 30            # 30ms chunks voor VAD (Silero recommended)
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5       # seconden stilte = einde opname
MIN_SPEECH_DURATION = 0.3    # minimale spraak om te accepteren
PRE_SPEECH_BUFFER = 0.3      # buffer voor pre-speech audio

# Audio gain (USB mic is zacht)
AUDIO_GAIN = 10.0  # +20dB

# Silero VAD model (v4 met h/c inputs)
VAD_MODEL_URL = "https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.onnx"
VAD_MODEL_PATH = os.path.expanduser("~/silero_vad_v4.onnx")

# Mock photo path
MOCK_PHOTO_PATH = Path(__file__).parent / "mock_photo.jpg"

# Stop commando
STOP_PHRASE = "stop nu het gesprek"

# Emotie emoji mapping
EMOTION_EMOJIS = {
    "happy": "😊", "sad": "😢", "angry": "😠",
    "surprised": "😲", "neutral": "😐", "curious": "🤔",
    "confused": "😕", "excited": "🤩", "thinking": "💭",
    "shy": "😳", "love": "😍", "tired": "😴",
    "bored": "😑", "proud": "😤", "worried": "😟"
}

# ============================================================================
# SILERO VAD (ONNX)
# ============================================================================

class SileroVAD:
    """Silero VAD v4 via ONNX Runtime."""

    def __init__(self):
        # Download model indien nodig
        if not os.path.exists(VAD_MODEL_PATH):
            print("📥 Downloading Silero VAD v4 model...")
            import urllib.request
            urllib.request.urlretrieve(VAD_MODEL_URL, VAD_MODEL_PATH)
            print("✅ Downloaded!")

        # Load ONNX model
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
        """Reset VAD state voor nieuwe opname."""
        self.h = np.zeros((2, 1, 64), dtype=np.float32)
        self.c = np.zeros((2, 1, 64), dtype=np.float32)
        self.sr = np.array(MODEL_SAMPLE_RATE, dtype=np.int64)

    def process(self, audio_chunk: np.ndarray) -> float:
        """Process audio chunk en return speech probability."""
        audio = (audio_chunk / 32767.0).astype(np.float32)
        audio = audio.reshape(1, -1)

        ort_inputs = {
            'input': audio,
            'h': self.h,
            'c': self.c,
            'sr': self.sr
        }

        out, h_out, c_out = self.session.run(None, ort_inputs)
        self.h = h_out
        self.c = c_out

        return out[0][0]


# ============================================================================
# AUDIO HELPERS
# ============================================================================

def enable_speaker():
    """Activeer speaker amplifier via GPIO 20."""
    try:
        subprocess.run(["pinctrl", "set", str(SPEAKER_GPIO), "op", "dh"],
                      check=True, capture_output=True)
        print(f"🔊 Speaker enabled (GPIO {SPEAKER_GPIO})")
    except FileNotFoundError:
        print("⚠️  pinctrl not found, speaker may not work")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not enable speaker GPIO: {e}")


def apply_gain(audio: np.ndarray, gain: float = AUDIO_GAIN) -> np.ndarray:
    """Apply gain to audio, clip to int16 range."""
    amplified = audio.astype(np.float32) * gain
    return np.clip(amplified, -32768, 32767).astype(np.int16)


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int = MODEL_SAMPLE_RATE) -> bytes:
    """Convert numpy int16 array to WAV bytes."""
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return buffer.getvalue()


def play_audio_base64(audio_base64: str, p: pyaudio.PyAudio) -> float:
    """
    Play base64 encoded WAV audio on speaker.
    Returns playback duration in seconds.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)

        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)

        stream = p.open(
            format=p.get_format_from_width(sample_width),
            channels=channels,
            rate=frame_rate,
            output=True,
            output_device_index=SPEAKER_DEVICE_INDEX
        )

        t_start = time.perf_counter()
        stream.write(frames)
        t_end = time.perf_counter()

        stream.stop_stream()
        stream.close()

        return t_end - t_start

    except Exception as e:
        print(f"⚠️  Audio playback error: {e}")
        return 0.0


# ============================================================================
# MOCK FUNCTION HANDLERS
# ============================================================================

def handle_mock_take_photo(arguments: dict) -> str:
    """
    Mock handler voor take_photo function call.
    Later te vervangen door echte camera integratie.
    """
    question = arguments.get("question", "wat zie je?")
    print(f"📷 [MOCK] take_photo aangeroepen: \"{question}\"")

    if MOCK_PHOTO_PATH.exists():
        print(f"   Mock foto: {MOCK_PHOTO_PATH}")
        return "Dit is een mock foto. Op de foto staan twee honden die vrolijk in de camera kijken."
    else:
        print(f"   ⚠️  Geen mock foto gevonden op {MOCK_PHOTO_PATH}")
        return "Mock: geen foto beschikbaar"


def handle_mock_show_emotion(arguments: dict, current_emotion: str) -> str:
    """
    Mock handler voor show_emotion function call.
    Later te vervangen door OLED display integratie.
    """
    new_emotion = arguments.get("emotion", "neutral")
    emoji = EMOTION_EMOJIS.get(new_emotion, "🤖")

    if new_emotion != current_emotion:
        print(f"🎭 [OLED] Emotie: {current_emotion} → {new_emotion} {emoji}")
    else:
        print(f"🎭 [OLED] Emotie: {new_emotion} {emoji} (unchanged)")

    return new_emotion


# ============================================================================
# WEBSOCKET CLIENT
# ============================================================================

async def send_audio_and_receive(
    audio_bytes: bytes,
    conversation_id: str = "pi-session"
) -> dict:
    """
    Send audio via WebSocket, receive response with full metadata.

    Returns dict with:
        - response_text: LLM response text
        - audio_chunks: list of audio chunks
        - function_calls: list of function calls
        - emotion: emotion info dict
        - timing_ms: timing dict from server
        - transcription: STT result
    """
    import websockets

    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

    message = {
        "type": "audio_process",
        "conversation_id": conversation_id,
        "timestamp": time.time(),
        "payload": {
            "audio_base64": audio_base64,
            "language": "nl"
        }
    }

    result = {
        "response_text": "",
        "audio_chunks": [],
        "function_calls": [],
        "emotion": {"current": "neutral", "changed": False},
        "timing_ms": {},
        "transcription": ""
    }

    try:
        async with websockets.connect(
            f"{WEBSOCKET_URL}?conversation_id={conversation_id}",
            ping_timeout=30
        ) as ws:
            # Send audio
            await ws.send(json.dumps(message))

            # Receive responses
            while True:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=60.0)
                    msg = json.loads(raw)
                    msg_type = msg.get("type", "")

                    if msg_type == "response":
                        payload = msg.get("payload", {})
                        result["response_text"] = payload.get("text", "")
                        result["function_calls"] = payload.get("function_calls", [])
                        result["emotion"] = payload.get("emotion", result["emotion"])
                        result["timing_ms"] = payload.get("timing_ms", {})
                        result["transcription"] = payload.get("transcription", "")

                    elif msg_type == "audio_chunk":
                        payload = msg.get("payload", {})
                        result["audio_chunks"].append({
                            "audio_base64": payload.get("audio_base64"),
                            "sentence": payload.get("sentence", ""),
                            "normalized": payload.get("normalized", ""),
                            "index": payload.get("index", 0),
                            "is_last": payload.get("is_last", False)
                        })
                        if payload.get("is_last", False):
                            break

                    elif msg_type == "error":
                        error = msg.get("payload", {}).get("error", "Unknown error")
                        print(f"❌ Server error: {error}")
                        break

                except asyncio.TimeoutError:
                    print("⚠️  Timeout waiting for response")
                    break

    except Exception as e:
        print(f"❌ WebSocket error: {e}")

    return result


# ============================================================================
# CONVERSATION FUNCTIONS
# ============================================================================

def wait_for_wake_word(p: pyaudio.PyAudio, wake_model) -> bool:
    """
    Wait for wake word to be detected.
    Opneemt op native mic rate, resamplet naar MODEL_SAMPLE_RATE voor wake word model.
    Returns True when detected, False on error.
    """
    # Bereken chunk size voor native mic sample rate (80ms)
    mic_chunk_size = int(MIC_SAMPLE_RATE * WAKE_CHUNK_MS / 1000)

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=MIC_SAMPLE_RATE,
        input=True,
        input_device_index=MIC_DEVICE_INDEX,
        frames_per_buffer=mic_chunk_size
    )

    print("\n🎧 Wachten op wake word... (zeg 'hey jarvis')")

    try:
        while True:
            data = stream.read(mic_chunk_size, exception_on_overflow=False)
            audio_chunk = np.frombuffer(data, dtype=np.int16)

            # Resample naar MODEL_SAMPLE_RATE (16kHz) voor wake word model
            if MIC_SAMPLE_RATE != MODEL_SAMPLE_RATE:
                audio_chunk = resample_audio(audio_chunk, MIC_SAMPLE_RATE, MODEL_SAMPLE_RATE)

            prediction = wake_model.predict(audio_chunk)
            score = prediction.get(WAKE_WORD, 0)

            if score > WAKE_THRESHOLD:
                print(f"✨ Wake word gedetecteerd! (score: {score:.2f})")
                stream.stop_stream()
                stream.close()
                return True

    except Exception as e:
        print(f"❌ Wake word error: {e}")
        stream.stop_stream()
        stream.close()
        return False


def record_speech(stream, vad: SileroVAD, pre_buffer: deque, mic_vad_chunk_size: int) -> tuple:
    """
    Record speech using VAD until silence detected.
    Opneemt op native mic rate, resamplet naar MODEL_SAMPLE_RATE voor VAD.
    Returns (audio_data at MIC_SAMPLE_RATE, duration_seconds).
    """
    vad.reset_state()

    # Bereken timing op basis van native mic sample rate
    chunks_per_second = MIC_SAMPLE_RATE / mic_vad_chunk_size
    silence_chunks = int(SILENCE_DURATION * chunks_per_second)
    min_speech_chunks = int(MIN_SPEECH_DURATION * chunks_per_second)

    is_speaking = False
    speech_chunks = 0
    silence_count = 0
    audio_buffer = []

    while True:
        data = stream.read(mic_vad_chunk_size, exception_on_overflow=False)
        audio_chunk = np.frombuffer(data, dtype=np.int16)

        # Resample naar MODEL_SAMPLE_RATE voor VAD model
        if MIC_SAMPLE_RATE != MODEL_SAMPLE_RATE:
            vad_chunk = resample_audio(audio_chunk, MIC_SAMPLE_RATE, MODEL_SAMPLE_RATE)
        else:
            vad_chunk = audio_chunk

        speech_prob = vad.process(vad_chunk)

        if speech_prob > VAD_THRESHOLD:
            if not is_speaking:
                print("🔴 Spraak gedetecteerd...")
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
                    else:
                        print("   (te kort, opnieuw)")
                        is_speaking = False
                        speech_chunks = 0
                        silence_count = 0
                        audio_buffer = []
            else:
                pre_buffer.append(data)

    all_audio = b''.join(audio_buffer)
    audio_data = np.frombuffer(all_audio, dtype=np.int16)
    duration = len(audio_data) / MIC_SAMPLE_RATE

    return audio_data, duration


def is_stop_command(text: str) -> bool:
    """Check of de tekst het stop commando bevat."""
    return STOP_PHRASE in text.lower()


# ============================================================================
# AUDIO DEVICE HELPERS
# ============================================================================

def resample_audio(audio: np.ndarray, orig_rate: int, target_rate: int) -> np.ndarray:
    """
    Resample audio van orig_rate naar target_rate.
    Simpele lineaire interpolatie - goed genoeg voor speech.

    Args:
        audio: int16 numpy array
        orig_rate: originele sample rate (bijv. 44100)
        target_rate: doel sample rate (bijv. 16000)

    Returns:
        Resampled int16 numpy array
    """
    if orig_rate == target_rate:
        return audio

    # Bereken nieuwe lengte
    duration = len(audio) / orig_rate
    new_length = int(duration * target_rate)

    # Lineaire interpolatie
    old_indices = np.linspace(0, len(audio) - 1, new_length)
    resampled = np.interp(old_indices, np.arange(len(audio)), audio.astype(np.float32))

    return resampled.astype(np.int16)


def find_device_by_name(p: pyaudio.PyAudio, name_pattern: str, need_input: bool = False, need_output: bool = False) -> tuple:
    """
    Find audio device by name pattern (case-insensitive substring match).

    Args:
        p: PyAudio instance
        name_pattern: Substring to search for in device name
        need_input: If True, device must have input channels
        need_output: If True, device must have output channels

    Returns:
        Tuple: (device_index, sample_rate, device_name) or (-1, 0, "") if not found
    """
    name_lower = name_pattern.lower()
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            device_name = info.get('name', '')

            if name_lower in device_name.lower():
                # Check channel requirements
                max_in = info.get('maxInputChannels', 0)
                max_out = info.get('maxOutputChannels', 0)

                if need_input and max_in == 0:
                    continue
                if need_output and max_out == 0:
                    continue

                sample_rate = int(info.get('defaultSampleRate', 44100))
                return (i, sample_rate, device_name)
        except Exception:
            continue
    return (-1, 0, "")


def list_audio_devices(p: pyaudio.PyAudio):
    """List all audio devices and their capabilities."""
    print("\n🔍 Audio Devices:")
    print("-" * 50)
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            name = info.get('name', 'Unknown')
            max_in = info.get('maxInputChannels', 0)
            max_out = info.get('maxOutputChannels', 0)
            rate = info.get('defaultSampleRate', 0)

            device_type = []
            if max_in > 0:
                device_type.append(f"IN:{max_in}ch")
            if max_out > 0:
                device_type.append(f"OUT:{max_out}ch")

            type_str = ", ".join(device_type) if device_type else "N/A"
            print(f"   [{i}] {name}")
            print(f"       {type_str}, {int(rate)}Hz")
        except Exception as e:
            print(f"   [{i}] Error: {e}")
    print("-" * 50)


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Terminal settings opslaan voor restore na Ctrl+C
    # (voorkomt dat keyboard niet meer werkt na afsluiten)
    old_term_settings = None
    if sys.stdin.isatty():
        old_term_settings = termios.tcgetattr(sys.stdin)

    print("=" * 60)
    print("🤖 Pi Conversation v2")
    print("=" * 60)
    print(f"Desktop: {DESKTOP_IP}")
    print(f"WebSocket: {WEBSOCKET_URL}")
    print(f"Wake word: {WAKE_WORD} (alleen bij start)")
    print(f"Mock foto: {MOCK_PHOTO_PATH}")
    print("=" * 60)
    print("Flow: Wake word → VAD loop (geen wake word meer nodig)")
    print(f"Stop: Zeg '{STOP_PHRASE}' of Ctrl+C")
    print("=" * 60)

    # Enable speaker
    enable_speaker()

    # Load wake word model
    print("\n🔄 Loading wake word model...")
    wake_model = WakeWordModel()
    print(f"✅ Models: {list(wake_model.models.keys())}")

    # Load VAD
    print("🔄 Loading Silero VAD...")
    vad = SileroVAD()
    print("✅ VAD loaded!")

    # PyAudio setup
    # Note: Je ziet ALSA/JACK warnings - deze zijn cosmetisch en niet kritiek
    print("🔄 Initializing audio...")
    p = pyaudio.PyAudio()
    print("✅ Audio initialized!")

    # Show available devices for debugging
    list_audio_devices(p)

    # Find devices by name (robuuster dan hardcoded indices)
    global MIC_DEVICE_INDEX, MIC_SAMPLE_RATE, SPEAKER_DEVICE_INDEX, SPEAKER_SAMPLE_RATE

    mic_result = find_device_by_name(p, MIC_DEVICE_NAME, need_input=True)
    spk_result = find_device_by_name(p, SPEAKER_DEVICE_NAME, need_output=True)

    MIC_DEVICE_INDEX, MIC_SAMPLE_RATE, mic_name = mic_result
    SPEAKER_DEVICE_INDEX, SPEAKER_SAMPLE_RATE, spk_name = spk_result

    print(f"\n📋 Gevonden devices:")
    if MIC_DEVICE_INDEX >= 0:
        print(f"   ✅ Mic [{MIC_DEVICE_INDEX}]: {mic_name}")
        print(f"      Native: {MIC_SAMPLE_RATE}Hz → Resample naar {MODEL_SAMPLE_RATE}Hz")
    else:
        print(f"   ❌ Mic niet gevonden (zoekterm: '{MIC_DEVICE_NAME}')")
        print("      Controleer of USB mic is aangesloten!")
        p.terminate()
        if old_term_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term_settings)
        return

    if SPEAKER_DEVICE_INDEX >= 0:
        print(f"   ✅ Speaker [{SPEAKER_DEVICE_INDEX}]: {spk_name}")
        print(f"      Native: {SPEAKER_SAMPLE_RATE}Hz")
    else:
        print(f"   ❌ Speaker niet gevonden (zoekterm: '{SPEAKER_DEVICE_NAME}')")
        print("      Controleer audio configuratie!")
        p.terminate()
        if old_term_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term_settings)
        return

    # Bereken chunk sizes voor de mic sample rate
    # Wake word: 80ms chunks, VAD: 30ms chunks
    mic_wake_chunk_size = int(MIC_SAMPLE_RATE * WAKE_CHUNK_MS / 1000)
    mic_vad_chunk_size = int(MIC_SAMPLE_RATE * VAD_CHUNK_MS / 1000)
    print(f"\n📊 Chunk sizes (bij {MIC_SAMPLE_RATE}Hz):")
    print(f"   Wake word: {mic_wake_chunk_size} samples ({WAKE_CHUNK_MS}ms)")
    print(f"   VAD: {mic_vad_chunk_size} samples ({VAD_CHUNK_MS}ms)")

    # Wait for wake word (eenmalig!)
    if not wait_for_wake_word(p, wake_model):
        print("❌ Wake word detectie mislukt")
        p.terminate()
        if old_term_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term_settings)
        return

    # Conversation state
    conversation_id = f"pi-{int(time.time())}"
    turn_count = 0
    current_emotion = "neutral"

    # Pre-buffer setup (op native mic rate)
    pre_buffer_chunks = int(PRE_SPEECH_BUFFER * MIC_SAMPLE_RATE / mic_vad_chunk_size)
    pre_buffer = deque(maxlen=pre_buffer_chunks)

    # Open stream voor VAD (op native mic rate)
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=MIC_SAMPLE_RATE,
        input=True,
        input_device_index=MIC_DEVICE_INDEX,
        frames_per_buffer=mic_vad_chunk_size
    )

    print("\n" + "=" * 60)
    print("🎙️ Conversatie gestart! Spreek wanneer je klaar bent.")
    print("   (geen wake word meer nodig)")
    print("=" * 60)

    try:
        while True:
            turn_count += 1
            print(f"\n{'─' * 60}")
            print(f"[Turn {turn_count}]")
            print("🎧 Luisteren... (spreek wanneer klaar)")

            # Record speech (returns audio at MIC_SAMPLE_RATE)
            t_record_start = time.perf_counter()
            audio_data, duration = record_speech(stream, vad, pre_buffer, mic_vad_chunk_size)
            t_record_end = time.perf_counter()

            print(f"✅ Opgenomen ({duration:.1f}s)")

            # Apply gain
            audio_data = apply_gain(audio_data)

            # Resample naar MODEL_SAMPLE_RATE voor STT
            if MIC_SAMPLE_RATE != MODEL_SAMPLE_RATE:
                audio_data = resample_audio(audio_data, MIC_SAMPLE_RATE, MODEL_SAMPLE_RATE)

            wav_bytes = audio_to_wav_bytes(audio_data, MODEL_SAMPLE_RATE)

            # Send to orchestrator
            print("📡 Versturen naar orchestrator...", end="", flush=True)
            t_send_start = time.perf_counter()
            result = asyncio.run(send_audio_and_receive(wav_bytes, conversation_id))
            t_send_end = time.perf_counter()
            print(" ✅")

            # Extract results
            transcription = result.get("transcription", "")
            response_text = result.get("response_text", "")
            function_calls = result.get("function_calls", [])
            emotion_info = result.get("emotion", {})
            timing_ms = result.get("timing_ms", {})
            audio_chunks = result.get("audio_chunks", [])

            # Show transcription
            if transcription:
                print(f"👤 Jij: {transcription}")

                # Check stop command
                if is_stop_command(transcription):
                    print("\n👋 Stop commando gedetecteerd. Tot ziens!")
                    break

            # Show tool calls with details
            if function_calls:
                print(f"🔧 [TOOL CALLS] {len(function_calls)} tool call(s):")
                for fc in function_calls:
                    name = fc.get("name", "")
                    args = fc.get("arguments", {})
                    print(f"   → {name}({args})")

                    # Mock handlers
                    if name == "take_photo":
                        mock_result = handle_mock_take_photo(args)
                        # Note: in reality, dit zou naar de LLM moeten voor verwerking
                    elif name == "show_emotion":
                        current_emotion = handle_mock_show_emotion(args, current_emotion)
            else:
                print("🔧 [TOOL CALLS] geen")

            # Show emotion state
            # emotion_info kan een dict of string zijn afhankelijk van orchestrator response
            if isinstance(emotion_info, dict):
                emotion = emotion_info.get("current", "neutral")
                changed = emotion_info.get("changed", False)
            else:
                emotion = emotion_info if emotion_info else "neutral"
                changed = False

            emoji = EMOTION_EMOJIS.get(emotion, "🤖")
            status = "VERANDERD" if changed else "behouden"
            print(f"🎭 [EMOTIE] {emotion} {emoji} ({status})")

            # Update current emotion for tracking
            if changed:
                current_emotion = emotion

            # Show response
            if response_text:
                print(f"🤖 NerdCarX: {response_text}")

            # Play audio chunks with timing
            tts_times = []
            for i, chunk in enumerate(audio_chunks):
                sentence = chunk.get("sentence", "")[:50]
                normalized = chunk.get("normalized", "")
                display = (normalized or sentence)[:50]

                print(f"🔊 [{i+1}] \"{display}...\"", end="", flush=True)

                if chunk.get("audio_base64"):
                    play_duration = play_audio_base64(chunk["audio_base64"], p)
                    tts_times.append(play_duration * 1000)
                    print(f" ({play_duration*1000:.0f}ms)")
                else:
                    print(" (geen audio)")

            # Timing summary
            stt_ms = timing_ms.get("stt", 0)
            llm_ms = timing_ms.get("llm", 0)
            tts_ms = timing_ms.get("tts", 0)
            total_playback = sum(tts_times)
            round_trip = (t_send_end - t_send_start) * 1000

            print(f"{'─' * 50}")
            print(f"⏱️  [TIMING]")
            print(f"    STT:      {stt_ms}ms")
            print(f"    LLM:      {llm_ms}ms")
            print(f"    TTS:      {tts_ms}ms")
            print(f"    Playback: {total_playback:.0f}ms ({len(tts_times)} chunks)")
            print(f"    ────────────────")
            print(f"    Round-trip: {round_trip:.0f}ms")

            # Clear pre-buffer voor volgende turn
            pre_buffer.clear()

    except KeyboardInterrupt:
        print("\n\n👋 Conversatie gestopt.")

    finally:
        # Cleanup audio
        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
        try:
            p.terminate()
        except Exception:
            pass

        # Terminal settings herstellen (voorkomt dat keyboard niet werkt)
        if old_term_settings is not None:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term_settings)
            except Exception:
                pass

        # Summary
        print(f"\n{'=' * 60}")
        print(f"📊 Samenvatting: {turn_count} turn(s)")
        print(f"Laatste emotie: {current_emotion} {EMOTION_EMOJIS.get(current_emotion, '🤖')}")
        print("=" * 60)


if __name__ == "__main__":
    main()
