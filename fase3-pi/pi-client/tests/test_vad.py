import pyaudio
import numpy as np
import onnxruntime
import urllib.request
import os

# Download Silero VAD ONNX model if not present
MODEL_PATH = os.path.expanduser("~/silero_vad.onnx")
if not os.path.exists(MODEL_PATH):
    print("Downloading Silero VAD model...")
    url = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Downloaded!")

# Load model
print("Loading Silero VAD...")
session = onnxruntime.InferenceSession(MODEL_PATH)
print("Loaded!")

# VAD state
h = np.zeros((2, 1, 64), dtype=np.float32)
c = np.zeros((2, 1, 64), dtype=np.float32)

def run_vad(audio_chunk):
    """Run VAD on 512 samples (32ms at 16kHz)"""
    global h, c

    # Normalize audio
    audio = audio_chunk.astype(np.float32) / 32768.0
    audio = audio.reshape(1, -1)

    # Run inference
    ort_inputs = {
        'input': audio,
        'h': h,
        'c': c,
        'sr': np.array([16000], dtype=np.int64)
    }
    ort_outs = session.run(None, ort_inputs)

    out, h, c = ort_outs[0], ort_outs[1], ort_outs[2]
    return out[0][0]

# Audio setup
audio = pyaudio.PyAudio()
CHUNK = 512  # 32ms at 16kHz
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=CHUNK, input_device_index=2)

print("Listening... Speak to see VAD scores (Ctrl+C to stop)")
print("Score > 0.5 = speech detected")
print("-" * 40)

try:
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        score = run_vad(data)

        # Visual indicator
        bar = "█" * int(score * 20)
        status = "SPEECH" if score > 0.5 else "      "
        print(f"\r{score:.2f} |{bar:<20}| {status}", end="", flush=True)

except KeyboardInterrupt:
    print("\nStopped")
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
