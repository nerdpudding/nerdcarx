import pyaudio
import numpy as np
import onnxruntime as ort
import urllib.request
import os

# Download older Silero VAD ONNX model (v4) that has simpler API
MODEL_PATH = os.path.expanduser("~/silero_vad_v4.onnx")
if not os.path.exists(MODEL_PATH):
    print("Downloading Silero VAD v4 model...")
    # v4 model with h/c state inputs
    url = "https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.onnx"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Downloaded!")

# Load model
print("Loading Silero VAD...")
sess_options = ort.SessionOptions()
sess_options.inter_op_num_threads = 1
sess_options.intra_op_num_threads = 1
session = ort.InferenceSession(MODEL_PATH, sess_options=sess_options,
                               providers=["CPUExecutionProvider"])

# Print inputs for debug
print("Model inputs:")
for inp in session.get_inputs():
    print(f"  {inp.name}: {inp.shape}")

# VAD state
h = np.zeros((2, 1, 64), dtype=np.float32)
c = np.zeros((2, 1, 64), dtype=np.float32)
sr = np.array(16000, dtype=np.int64)

def run_vad(audio_chunk):
    """Run VAD on audio chunk"""
    global h, c

    # Normalize to float32 [-1, 1]
    audio = (audio_chunk / 32767.0).astype(np.float32)
    audio = audio.reshape(1, -1)

    ort_inputs = {
        'input': audio,
        'h': h,
        'c': c,
        'sr': sr
    }

    out, h_out, c_out = session.run(None, ort_inputs)
    h = h_out
    c = c_out

    return out[0][0]

# Audio setup
SAMPLE_RATE = 16000
CHUNK = 480  # 30ms at 16kHz (recommended for Silero)

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE,
                    input=True, frames_per_buffer=CHUNK, input_device_index=2)

print("Loaded!")
print("Listening... Speak to see VAD scores (Ctrl+C to stop)")
print("Score > 0.5 = speech detected")
print("-" * 40)

try:
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        level = np.abs(data).mean()
        score = run_vad(data)

        bar = "█" * int(score * 20)
        status = "SPEECH" if score > 0.5 else "      "
        print(f"\r{score:.2f} |{bar:<20}| {status} lvl:{level:.0f}", end="", flush=True)

except KeyboardInterrupt:
    print("\nStopped")
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
