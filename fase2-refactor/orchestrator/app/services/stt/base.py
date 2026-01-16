"""STT Provider protocol."""
from typing import Protocol, runtime_checkable


@runtime_checkable
class STTProvider(Protocol):
    """
    Protocol voor Speech-to-Text providers.

    Implementaties:
    - VoxtralSTT (Voxtral Mini via vLLM)
    - Toekomst: WhisperSTT, DeepgramSTT, etc.
    """

    async def transcribe(self, audio: bytes, language: str = "nl") -> str:
        """
        Transcribeer audio naar tekst.

        Args:
            audio: Audio bytes (WAV format expected)
            language: Taalcode (default: nl)

        Returns:
            Getranscribeerde tekst
        """
        ...

    async def health_check(self) -> bool:
        """Check of de STT service beschikbaar is."""
        ...
