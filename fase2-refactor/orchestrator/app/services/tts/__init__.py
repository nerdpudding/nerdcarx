"""Text-to-Speech services."""
from .base import TTSProvider, TTSResult
from .fishaudio import FishAudioTTS

__all__ = ["TTSProvider", "TTSResult", "FishAudioTTS"]
