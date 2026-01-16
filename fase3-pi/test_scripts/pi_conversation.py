#!/usr/bin/env python3
"""
Pi Conversation - Wake Word + VAD + WebSocket naar Desktop Orchestrator

Flow:
    [Wake word "hey jarvis"] -> [VAD opname] -> [WebSocket] -> [Desktop STT/LLM/TTS] -> [Speaker]

Configuratie:
    DESKTOP_IP = "192.168.1.161"  # Desktop waar orchestrator draait
    MIC_DEVICE = 2                # USB mic (card 2)
    SPEAKER_DEVICE = 3            # I2S speaker (card 3)

Gebruik op Pi:
    conda activate nerdcarx
    python pi_conversation.py
"""

import asyncio
import base64
import io
import json
import os
import subprocess
import time
import wave

import numpy as np
import onnxruntime as ort
import pyaudio
from openwakeword.model import Model as WakeWordModel

# ============================================================================
# CONFIGURATIE
# ============================================================================

# Network
DESKTOP_IP = "192.168.1.161"
WEBSOCKET_URL = f"ws://{DESKTOP_IP}:8200/ws"

# Audio hardware (Pi specifiek)
MIC_DEVICE_INDEX = 2      # USB mic (card 2)
SPEAKER_DEVICE_INDEX = 3  # I2S speaker (card 3)
SPEAKER_GPIO = 20         # GPIO pin voor amplifier enable

# Audio parameters
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Wake word
WAKE_WORD = "hey_jarvis"
WAKE_THRESHOLD = 0.5
WAKE_CHUNK_SIZE = 1280  # 80ms @ 16kHz

# VAD parameters
VAD_CHUNK_SIZE = 480    # 30ms @ 16kHz (Silero recommended)
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5  # seconden stilte = einde opname
MIN_SPEECH_DURATION = 0.3  # minimale spraak om te accepteren
PRE_SPEECH_BUFFER = 0.3  # buffer voor wake word

# Audio gain (USB mic is zacht)
AUDIO_GAIN = 10.0  # +20dB

# Silero VAD model (v4 met h/c inputs)
VAD_MODEL_URL = "https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.onnx"
VAD_MODEL_PATH = os.path.expanduser("~/silero_vad_v4.onnx")

# ============================================================================
# SILERO VAD (ONNX)
# ============================================================================

class SileroVAD:
    """Silero VAD v4 via ONNX Runtime."""

    def __init__(self):
        # Download model indien nodig
        if not os.path.exists(VAD_MODEL_PATH):
            print("Downloading Silero VAD v4 model...")
            import urllib.request
            urllib.request.urlretrieve(VAD_MODEL_URL, VAD_MODEL_PATH)
            print("Downloaded!")

        # Load ONNX model
        sess_options = ort.SessionOptions()
        sess_options.inter_op_num_threads = 1
        sess_options.intra_op_num_threads = 1
        self.session = ort.InferenceSession(
            VAD_MODEL_PATH,
            sess_options=sess_options,
            providers=["CPUExecutionProvider"]
        )

        # VAD state (v4 model: h/c met shape 2,1,64)
        self.reset_state()

    def reset_state(self):
        """Reset VAD state voor nieuwe opname."""
        self.h = np.zeros((2, 1, 64), dtype=np.float32)
        self.c = np.zeros((2, 1, 64), dtype=np.float32)
        self.sr = np.array(SAMPLE_RATE, dtype=np.int64)

    def process(self, audio_chunk: np.ndarray) -> float:
        """
        Process audio chunk en return speech probability.

        Args:
            audio_chunk: int16 numpy array

        Returns:
            float: speech probability 0-1
        """
        # Normalize naar float32 [-1, 1]
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
        print(f"Speaker enabled (GPIO {SPEAKER_GPIO})")
    except FileNotFoundError:
        print("WARNING: pinctrl not found, speaker may not work")
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Could not enable speaker GPIO: {e}")


def apply_gain(audio: np.ndarray, gain: float = AUDIO_GAIN) -> np.ndarray:
    """Apply gain to audio, clip to int16 range."""
    amplified = audio.astype(np.float32) * gain
    return np.clip(amplified, -32768, 32767).astype(np.int16)


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Convert numpy int16 array to WAV bytes."""
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return buffer.getvalue()


def play_audio_base64(audio_base64: str, p: pyaudio.PyAudio):
    """
    Play base64 encoded WAV audio on speaker.

    Args:
        audio_base64: base64 encoded WAV data
        p: PyAudio instance
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)

        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

        stream = p.open(
            format=p.get_format_from_width(sample_width),
            channels=channels,
            rate=frame_rate,
            output=True,
            output_device_index=SPEAKER_DEVICE_INDEX
        )

        stream.write(frames)
        stream.stop_stream()
        stream.close()

    except Exception as e:
        print(f"Audio playback error: {e}")


# ============================================================================
# WEBSOCKET CLIENT
# ============================================================================

async def send_audio_and_receive(
    audio_bytes: bytes,
    conversation_id: str = "pi-session"
) -> tuple:
    """
    Send audio via WebSocket, receive response.

    Args:
        audio_bytes: WAV audio bytes
        conversation_id: conversation identifier

    Returns:
        tuple: (response_text, audio_chunks, function_calls)
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

    response_text = ""
    audio_chunks = []
    function_calls = []

    try:
        async with websockets.connect(
            f"{WEBSOCKET_URL}?conversation_id={conversation_id}"
        ) as ws:
            # Send audio
            await ws.send(json.dumps(message))

            # Receive responses until done
            while True:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    msg = json.loads(raw)
                    msg_type = msg.get("type", "")

                    if msg_type == "response":
                        payload = msg.get("payload", {})
                        response_text = payload.get("text", "")
                        function_calls = payload.get("function_calls", [])
                        # Response komt vaak als laatste, maar audio_chunks kunnen nog volgen

                    elif msg_type == "audio_chunk":
                        payload = msg.get("payload", {})
                        audio_chunks.append({
                            "audio_base64": payload.get("audio_base64"),
                            "sentence": payload.get("sentence", ""),
                            "index": payload.get("index", 0),
                            "is_last": payload.get("is_last", False)
                        })
                        # Als is_last, zijn we klaar
                        if payload.get("is_last", False):
                            break

                    elif msg_type == "error":
                        error = msg.get("payload", {}).get("error", "Unknown error")
                        print(f"Server error: {error}")
                        break

                except asyncio.TimeoutError:
                    print("Timeout waiting for response")
                    break

    except Exception as e:
        print(f"WebSocket error: {e}")

    return response_text, audio_chunks, function_calls


# ============================================================================
# MAIN CONVERSATION LOOP
# ============================================================================

def record_speech(stream, vad: SileroVAD, pre_buffer: list) -> np.ndarray:
    """
    Record speech using VAD until silence detected.

    Args:
        stream: PyAudio input stream
        vad: SileroVAD instance
        pre_buffer: pre-speech audio buffer (from wake word detection)

    Returns:
        numpy array of recorded audio (int16)
    """
    vad.reset_state()

    # Timing calculations
    chunks_per_second = SAMPLE_RATE / VAD_CHUNK_SIZE
    silence_chunks = int(SILENCE_DURATION * chunks_per_second)
    min_speech_chunks = int(MIN_SPEECH_DURATION * chunks_per_second)

    is_speaking = False
    speech_chunks = 0
    silence_count = 0
    audio_buffer = []

    print("Listening for speech...")

    while True:
        data = stream.read(VAD_CHUNK_SIZE, exception_on_overflow=False)
        audio_chunk = np.frombuffer(data, dtype=np.int16)
        speech_prob = vad.process(audio_chunk)

        if speech_prob > VAD_THRESHOLD:
            if not is_speaking:
                print("Speech detected!")
                is_speaking = True
                # Include pre-buffer
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
                        # Voldoende spraak opgenomen
                        break
                    else:
                        # Te kort, reset
                        print("Too short, continuing...")
                        is_speaking = False
                        speech_chunks = 0
                        silence_count = 0
                        audio_buffer = []

    # Combine all chunks
    all_audio = b''.join(audio_buffer)
    return np.frombuffer(all_audio, dtype=np.int16)


def main():
    print("=" * 60)
    print("Pi Conversation")
    print("=" * 60)
    print(f"Desktop: {DESKTOP_IP}")
    print(f"WebSocket: {WEBSOCKET_URL}")
    print(f"Wake word: {WAKE_WORD}")
    print("=" * 60)

    # Enable speaker
    enable_speaker()

    # Load wake word model
    print("Loading wake word model...")
    wake_model = WakeWordModel()
    print(f"Models loaded: {list(wake_model.models.keys())}")

    # Load VAD
    print("Loading Silero VAD...")
    vad = SileroVAD()
    print("VAD loaded!")

    # PyAudio setup
    p = pyaudio.PyAudio()

    # Open mic stream (wake word chunk size)
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=MIC_DEVICE_INDEX,
        frames_per_buffer=WAKE_CHUNK_SIZE
    )

    # Pre-speech buffer
    pre_buffer_chunks = int(PRE_SPEECH_BUFFER * SAMPLE_RATE / WAKE_CHUNK_SIZE)
    pre_buffer = []

    conversation_id = f"pi-{int(time.time())}"
    turn_count = 0

    print("\nReady! Say 'hey jarvis' to start...")
    print("Ctrl+C to quit\n")

    try:
        while True:
            # Listen for wake word
            data = stream.read(WAKE_CHUNK_SIZE, exception_on_overflow=False)
            audio_chunk = np.frombuffer(data, dtype=np.int16)

            # Update pre-buffer
            pre_buffer.append(data)
            if len(pre_buffer) > pre_buffer_chunks:
                pre_buffer.pop(0)

            # Check wake word
            prediction = wake_model.predict(audio_chunk)
            score = prediction.get(WAKE_WORD, 0)

            if score > WAKE_THRESHOLD:
                turn_count += 1
                print(f"\n[Turn {turn_count}] Wake word detected! (score: {score:.2f})")

                # Switch to VAD chunk size for recording
                stream.stop_stream()
                stream.close()
                stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    input_device_index=MIC_DEVICE_INDEX,
                    frames_per_buffer=VAD_CHUNK_SIZE
                )

                # Record speech with VAD
                audio_data = record_speech(stream, vad, pre_buffer)
                duration = len(audio_data) / SAMPLE_RATE
                print(f"Recorded {duration:.1f}s")

                # Apply gain
                audio_data = apply_gain(audio_data)

                # Convert to WAV
                wav_bytes = audio_to_wav_bytes(audio_data)

                # Send via WebSocket
                print("Sending to orchestrator...")
                response_text, audio_chunks, function_calls = asyncio.run(
                    send_audio_and_receive(wav_bytes, conversation_id)
                )

                # Show response
                if response_text:
                    print(f"Response: {response_text}")

                if function_calls:
                    print(f"Function calls: {function_calls}")

                # Play audio chunks
                for chunk in audio_chunks:
                    sentence = chunk.get("sentence", "")[:40]
                    print(f"Playing: \"{sentence}...\"")
                    if chunk.get("audio_base64"):
                        play_audio_base64(chunk["audio_base64"], p)

                # Switch back to wake word chunk size
                stream.stop_stream()
                stream.close()
                stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    input_device_index=MIC_DEVICE_INDEX,
                    frames_per_buffer=WAKE_CHUNK_SIZE
                )

                # Clear pre-buffer
                pre_buffer = []

                print("\nListening for wake word...")

    except KeyboardInterrupt:
        print("\n\nStopped.")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print(f"Turns: {turn_count}")


if __name__ == "__main__":
    main()
