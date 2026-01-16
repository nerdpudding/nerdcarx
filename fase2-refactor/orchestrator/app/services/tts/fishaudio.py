"""Fish Audio TTS implementation."""
import base64
from typing import Optional

import httpx

from .base import TTSResult
from ...utils.text_normalization import normalize_for_tts


class FishAudioTTS:
    """
    Fish Audio S1-mini TTS service.

    Features:
    - Nederlandse reference voice
    - Text normalization voor betere uitspraak
    - Streaming per zin mogelijk
    """

    def __init__(
        self,
        url: str = "http://localhost:8250",
        reference_id: str = "dutch2",
        temperature: float = 0.5,
        top_p: float = 0.6,
        format: str = "wav",
        timeout: float = 30.0,
        normalize_text: bool = True
    ):
        self.url = url.rstrip("/")
        self.reference_id = reference_id
        self.temperature = temperature
        self.top_p = top_p
        self.format = format
        self.timeout = timeout
        self.normalize_text = normalize_text

    async def synthesize(
        self,
        text: str,
        reference_id: Optional[str] = None
    ) -> TTSResult:
        """
        Syntheseer tekst naar spraak.

        Args:
            text: Tekst om te synthesiseren
            reference_id: Voice reference override

        Returns:
            TTSResult met audio bytes en optionele normalized text
        """
        if not text.strip():
            return TTSResult(audio_bytes=b"", normalized_text=None)

        # Normaliseer tekst voor betere uitspraak
        original_text = text
        if self.normalize_text:
            text = normalize_for_tts(text)

        payload = {
            "text": text,
            "reference_id": reference_id or self.reference_id,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "format": self.format
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.url}/v1/tts",
                json=payload
            )
            resp.raise_for_status()

        # Return normalized text alleen als het verschilt
        normalized = text if text != original_text else None

        return TTSResult(
            audio_bytes=resp.content,
            format=self.format,
            normalized_text=normalized
        )

    async def synthesize_base64(
        self,
        text: str,
        reference_id: Optional[str] = None
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Syntheseer tekst en return base64 encoded audio.

        Convenience method voor API responses.

        Returns:
            (base64_audio, normalized_text) of (None, None) bij lege tekst/fout
        """
        try:
            result = await self.synthesize(text, reference_id)
            if not result.audio_bytes:
                return None, None
            audio_b64 = base64.b64encode(result.audio_bytes).decode("utf-8")
            return audio_b64, result.normalized_text
        except Exception:
            return None, None

    async def health_check(self) -> bool:
        """Check of Fish Audio beschikbaar is."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.url}/v1/health")
                return resp.status_code == 200
        except Exception:
            return False
