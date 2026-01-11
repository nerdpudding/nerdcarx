#!/usr/bin/env python3
"""
NerdCarX TTS Service - Chatterbox Multilingual

FastAPI service voor Text-to-Speech met emotie-expressie.

Gebruik:
    conda activate nerdcarx-tts
    uvicorn tts_service:app --port 8250
"""

import io
import wave
from pathlib import Path
from typing import Optional

import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

# Lazy loading - model wordt geladen bij eerste request of startup
model = None
MODEL_SR = 22050  # Chatterbox sample rate

# Emotie → TTS parameters mapping
EMOTION_PARAMS = {
    "neutral": {"exaggeration": 0.5, "cfg_weight": 0.5},
    "happy": {"exaggeration": 0.7, "cfg_weight": 0.4},
    "excited": {"exaggeration": 0.9, "cfg_weight": 0.3},
    "sad": {"exaggeration": 0.6, "cfg_weight": 0.5},
    "angry": {"exaggeration": 0.8, "cfg_weight": 0.4},
    "surprised": {"exaggeration": 0.8, "cfg_weight": 0.4},
    "curious": {"exaggeration": 0.6, "cfg_weight": 0.5},
    "confused": {"exaggeration": 0.5, "cfg_weight": 0.5},
    "thinking": {"exaggeration": 0.4, "cfg_weight": 0.6},
    "shy": {"exaggeration": 0.4, "cfg_weight": 0.5},
    "love": {"exaggeration": 0.7, "cfg_weight": 0.4},
    "tired": {"exaggeration": 0.3, "cfg_weight": 0.6},
    "bored": {"exaggeration": 0.3, "cfg_weight": 0.6},
    "proud": {"exaggeration": 0.7, "cfg_weight": 0.4},
    "worried": {"exaggeration": 0.5, "cfg_weight": 0.5},
}

# Default parameters
DEFAULT_EXAGGERATION = 0.5
DEFAULT_CFG_WEIGHT = 0.5

# Voice reference path (optional)
VOICE_REFERENCE_PATH = Path(__file__).parent / "voice_reference.wav"

app = FastAPI(
    title="NerdCarX TTS Service",
    description="Chatterbox Multilingual TTS met emotie-expressie",
    version="0.1.0"
)


class SynthesizeRequest(BaseModel):
    """Request voor synthesize endpoint."""
    text: str
    emotion: Optional[str] = "neutral"
    exaggeration: Optional[float] = None  # Override emotie mapping
    cfg_weight: Optional[float] = None    # Override emotie mapping


def load_model():
    """Laad het TTS model (lazy loading)."""
    global model, MODEL_SR
    if model is None:
        print("Loading Chatterbox Multilingual model...")
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = ChatterboxMultilingualTTS.from_pretrained(device=device)
        MODEL_SR = model.sr
        print(f"Model loaded on {device}")
    return model


def tensor_to_wav_bytes(wav_tensor: torch.Tensor, sample_rate: int) -> bytes:
    """Converteer PyTorch tensor naar WAV bytes."""
    # Tensor naar numpy
    if wav_tensor.dim() == 2:
        wav_np = wav_tensor[0].cpu().numpy()
    else:
        wav_np = wav_tensor.cpu().numpy()

    # Normaliseer naar int16
    wav_int16 = (wav_np * 32767).astype("int16")

    # Schrijf naar WAV buffer
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(wav_int16.tobytes())

    return buffer.getvalue()


@app.on_event("startup")
async def startup_event():
    """Laad model bij startup voor snellere eerste request."""
    load_model()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "tts",
        "model": "chatterbox-multilingual",
        "model_loaded": model is not None,
        "cuda_available": torch.cuda.is_available()
    }


@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    Genereer spraak van tekst.

    Returns: audio/wav bytes
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    # Laad model indien nodig
    tts_model = load_model()

    # Bepaal parameters
    emotion = request.emotion or "neutral"
    emotion_params = EMOTION_PARAMS.get(emotion, EMOTION_PARAMS["neutral"])

    exaggeration = request.exaggeration if request.exaggeration is not None else emotion_params["exaggeration"]
    cfg_weight = request.cfg_weight if request.cfg_weight is not None else emotion_params["cfg_weight"]

    # Voice reference (optioneel)
    audio_prompt_path = None
    if VOICE_REFERENCE_PATH.exists():
        audio_prompt_path = str(VOICE_REFERENCE_PATH)

    try:
        # Genereer audio
        wav = tts_model.generate(
            text=request.text,
            language_id="nl",
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            audio_prompt_path=audio_prompt_path
        )

        # Converteer naar WAV bytes
        wav_bytes = tensor_to_wav_bytes(wav, MODEL_SR)

        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={
                "X-Emotion": emotion,
                "X-Exaggeration": str(exaggeration),
                "X-CFG-Weight": str(cfg_weight)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.get("/emotions")
async def list_emotions():
    """Toon beschikbare emoties en hun parameters."""
    return {
        "emotions": EMOTION_PARAMS,
        "default_exaggeration": DEFAULT_EXAGGERATION,
        "default_cfg_weight": DEFAULT_CFG_WEIGHT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8250)
