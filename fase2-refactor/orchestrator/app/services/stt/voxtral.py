"""Voxtral STT implementation via vLLM."""
import base64
from typing import Optional

import httpx


class VoxtralSTT:
    """
    Voxtral Mini 3B STT via vLLM OpenAI-compatible API.

    Features:
    - OpenAI-compatible endpoint
    - Audio transcription met Mistral's Voxtral model
    """

    def __init__(
        self,
        url: str = "http://localhost:8150",
        model: str = "mistralai/Voxtral-Mini-3B-2507",
        temperature: float = 0.0,
        timeout: float = 60.0
    ):
        self.url = url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    async def transcribe(self, audio: bytes, language: str = "nl") -> str:
        """
        Transcribeer audio naar tekst via Voxtral.

        Args:
            audio: WAV audio bytes
            language: Taalcode (gebruikt in prompt hint)

        Returns:
            Getranscribeerde tekst

        Raises:
            httpx.HTTPError: Bij verbindingsfouten
        """
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio).decode("utf-8")
        audio_url = f"data:audio/wav;base64,{audio_base64}"

        # Build messages met audio content
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "audio_url",
                        "audio_url": {"url": audio_url}
                    },
                    {
                        "type": "text",
                        "text": f"Transcribe this audio. The language is {language}."
                    }
                ]
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.url}/v1/chat/completions",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()

        # Extract transcription from response
        return result["choices"][0]["message"]["content"]

    async def health_check(self) -> bool:
        """Check of Voxtral service beschikbaar is."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.url}/health")
                return resp.status_code == 200
        except Exception:
            return False

    async def get_models(self) -> Optional[list[str]]:
        """Haal beschikbare modellen op."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.url}/v1/models")
                resp.raise_for_status()
                result = resp.json()
                return [m["id"] for m in result.get("data", [])]
        except Exception:
            return None
