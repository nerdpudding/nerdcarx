#!/usr/bin/env python3
"""
Test script voor Chatterbox Multilingual TTS.
Test Nederlandse spraaksynthese met emotie parameters.

Gebruik:
    conda activate nerdcarx-tts
    python test_chatterbox.py
"""

import torch
import torchaudio as ta
from pathlib import Path

# Check CUDA
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

print("\n" + "="*60)
print("Chatterbox Multilingual TTS Test")
print("="*60)

# Lazy import - triggers model download
print("\n[1/4] Model laden (eerste keer: download ~2GB)...")
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[2/4] Model initialiseren op {device}...")
model = ChatterboxMultilingualTTS.from_pretrained(device=device)
print("Model geladen!")

# Test zinnen met verschillende emotie niveaus
test_cases = [
    {
        "text": "Hallo, ik ben NerdCarX, een slimme robotauto.",
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
        "description": "neutral"
    },
    {
        "text": "Wat leuk dat je met me wilt praten! Dit is echt geweldig!",
        "exaggeration": 0.8,
        "cfg_weight": 0.3,
        "description": "happy/excited"
    },
    {
        "text": "Oh, dat is jammer. Ik voel me een beetje verdrietig.",
        "exaggeration": 0.6,
        "cfg_weight": 0.5,
        "description": "sad"
    },
    {
        "text": "Hmm, ik weet niet zeker wat je bedoelt. Kun je dat uitleggen?",
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
        "description": "curious/confused"
    }
]

# Output folder
output_dir = Path(__file__).parent / "test_output"
output_dir.mkdir(exist_ok=True)

print(f"\n[3/4] {len(test_cases)} test zinnen genereren...")
print(f"Output folder: {output_dir}\n")

for i, tc in enumerate(test_cases, 1):
    print(f"  [{i}/{len(test_cases)}] {tc['description']}...")
    print(f"      Text: \"{tc['text'][:50]}...\"" if len(tc['text']) > 50 else f"      Text: \"{tc['text']}\"")
    print(f"      exaggeration={tc['exaggeration']}, cfg_weight={tc['cfg_weight']}")

    # Generate audio
    wav = model.generate(
        text=tc['text'],
        language_id="nl",
        exaggeration=tc['exaggeration'],
        cfg_weight=tc['cfg_weight']
    )

    # Save
    filename = f"test_{i}_{tc['description'].replace('/', '_')}.wav"
    filepath = output_dir / filename
    ta.save(str(filepath), wav, model.sr)
    print(f"      Saved: {filename}")

print(f"\n[4/4] Klaar!")
print(f"\nAlle output bestanden staan in: {output_dir}")
print("\nLuister naar de bestanden om de kwaliteit te beoordelen:")
for i, tc in enumerate(test_cases, 1):
    filename = f"test_{i}_{tc['description'].replace('/', '_')}.wav"
    print(f"  - {filename}: {tc['description']}")
