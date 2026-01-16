"""TTS Provider protocol."""
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable


@dataclass
class TTSResult:
    """Result van TTS synthesis."""
    audio_bytes: bytes
    format: str = "wav"
    normalized_text: Optional[str] = None


@runtime_checkable
class TTSProvider(Protocol):
    """
    Protocol voor Text-to-Speech providers.

    Implementaties:
    - FishAudioTTS (Fish Audio S1-mini)
    - Toekomst: ElevenLabsTTS, etc.
    """

    async def synthesize(
        self,
        text: str,
        reference_id: Optional[str] = None
    ) -> TTSResult:
        """
        Synthetiseer tekst naar spraak.

        Args:
            text: Tekst om te synthesiseren
            reference_id: Optionele voice reference

        Returns:
            TTSResult met audio bytes
        """
        ...

    async def health_check(self) -> bool:
        """Check of de TTS service beschikbaar is."""
        ...
