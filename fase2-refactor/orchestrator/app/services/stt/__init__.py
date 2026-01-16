"""Speech-to-Text services."""
from .base import STTProvider
from .voxtral import VoxtralSTT

__all__ = ["STTProvider", "VoxtralSTT"]
