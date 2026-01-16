"""Vision tool voor camera functionaliteit."""
import base64
from pathlib import Path
from typing import Optional

import httpx


class VisionTool:
    """
    take_photo tool - maakt foto en analyseert deze.

    Ondersteunt:
    - Mock image voor desktop testing
    - Pi camera endpoint (toekomst)
    """

    def __init__(
        self,
        mock_image_path: Optional[str] = None,
        pi_camera_url: Optional[str] = None,
        llm_url: str = "http://localhost:11434",
        llm_model: str = "ministral-3:14b"
    ):
        self.mock_image_path = Path(mock_image_path) if mock_image_path else None
        self.pi_camera_url = pi_camera_url
        self.llm_url = llm_url
        self.llm_model = llm_model

    @property
    def name(self) -> str:
        return "take_photo"

    @property
    def definition(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "take_photo",
                "description": "Maak een foto met de camera en analyseer wat je ziet. Gebruik bij vragen als 'wat zie je?', 'beschrijf je omgeving', of andere visuele vragen.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "De vraag over wat je moet analyseren in de foto"
                        }
                    },
                    "required": ["question"]
                }
            }
        }

    async def _get_image(self) -> Optional[str]:
        """
        Haal image op als base64.

        Returns:
            Base64 encoded image of None
        """
        # Probeer Pi camera eerst
        if self.pi_camera_url:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(self.pi_camera_url)
                    resp.raise_for_status()
                    return base64.b64encode(resp.content).decode("utf-8")
            except Exception:
                pass  # Fall back to mock

        # Mock image
        if self.mock_image_path and self.mock_image_path.exists():
            with open(self.mock_image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

        return None

    async def execute(self, arguments: dict, context: Optional[dict] = None) -> str:
        """
        Maak foto en analyseer.

        Args:
            arguments: {"question": "..."}
            context: Optionele context met llm_client

        Returns:
            Analyse resultaat
        """
        question = arguments.get("question", "Beschrijf wat je ziet.")

        # Haal image
        image_base64 = await self._get_image()
        if not image_base64:
            return "Geen camera beschikbaar - kan geen foto maken."

        # Analyseer met vision LLM
        messages = [
            {
                "role": "system",
                "content": "Je bent de camera van een robot. Beschrijf feitelijk wat je ziet."
            },
            {
                "role": "user",
                "content": question,
                "images": [image_base64]
            }
        ]

        payload = {
            "model": self.llm_model,
            "messages": messages,
            "stream": False,
            "keep_alive": -1,
            "options": {"temperature": 0.15}
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.llm_url}/api/chat",
                    json=payload
                )
                resp.raise_for_status()
                result = resp.json()
                return result["message"].get("content", "Kon de foto niet analyseren.")
        except Exception as e:
            return f"Fout bij foto analyse: {str(e)}"
