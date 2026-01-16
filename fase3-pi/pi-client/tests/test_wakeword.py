import pyaudio
import numpy as np
from openwakeword.model import Model

# v0.4.0 API - load all models, no kwargs
model = Model()

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280, input_device_index=2)

print(f"Loaded models: {list(model.models.keys())}")
print("Listening for 'hey jarvis'... (Ctrl+C to stop)")

while True:
    data = np.frombuffer(stream.read(1280), dtype=np.int16)
    prediction = model.predict(data)
    score = prediction["hey_jarvis"]
    if score > 0.5:
        print(f"DETECTED! Score: {score:.2f}")
