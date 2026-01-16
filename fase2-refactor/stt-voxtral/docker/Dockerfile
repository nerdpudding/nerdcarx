# Custom vLLM image met audio dependencies voor Voxtral
#
# De standaard vllm/vllm-openai image mist audio dependencies.
# Deze Dockerfile installeert alles wat nodig is voor Voxtral STT.

FROM vllm/vllm-openai:nightly

# Installeer system dependencies voor audio processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Installeer Python audio dependencies
# - vllm[audio]: librosa en andere audio processing libs
# - mistral-common[audio]: soundfile voor Mistral audio models
RUN pip install --no-cache-dir \
    "vllm[audio]" \
    soundfile \
    librosa \
    "mistral-common[audio]"
