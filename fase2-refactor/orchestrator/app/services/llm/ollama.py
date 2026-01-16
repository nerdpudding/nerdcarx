"""Ollama LLM implementation."""
import json
import re
from typing import Optional

import httpx

from .base import LLMResponse


class OllamaLLM:
    """
    Ollama LLM service met Ministral model.

    Features:
    - Native tool calling support
    - Fallback text-based tool parsing
    - Vision support (images in messages)
    """

    def __init__(
        self,
        url: str = "http://localhost:11434",
        model: str = "ministral-3:14b",
        temperature: float = 0.15,
        top_p: float = 1.0,
        repeat_penalty: float = 1.0,
        num_ctx: int = 65536,
        timeout: float = 120.0
    ):
        self.url = url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.repeat_penalty = repeat_penalty
        self.num_ctx = num_ctx
        self.timeout = timeout

    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        temperature: Optional[float] = None,
        num_ctx: Optional[int] = None
    ) -> LLMResponse:
        """
        Stuur chat request naar Ollama.

        Args:
            messages: Messages in Ollama format
            tools: Tool definitions
            temperature: Temperature override
            num_ctx: Context window override

        Returns:
            LLMResponse met content en tool calls
        """
        options = {
            "temperature": temperature or self.temperature,
            "top_p": self.top_p,
            "repeat_penalty": self.repeat_penalty,
            "num_ctx": num_ctx or self.num_ctx
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": -1,
            "options": options
        }

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.url}/api/chat",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()

        message = result.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        # Als geen native tool calls, check voor text-based
        if not tool_calls and content:
            content, parsed_calls = self._parse_text_tool_calls(content)
            if parsed_calls:
                tool_calls = parsed_calls

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            model=self.model,
            done=True
        )

    def _parse_text_tool_calls(self, content: str) -> tuple[str, list[dict]]:
        """
        Parse tool calls uit tekst (Mistral format).

        Format: functionname[ARGS]{json}

        Returns:
            (cleaned_content, list of tool_call dicts)
        """
        pattern = r'(\w+)\[ARGS\](\{[^}]+\})'
        matches = re.findall(pattern, content)

        tool_calls = []
        for name, args_str in matches:
            try:
                args = json.loads(args_str)
                tool_calls.append({
                    "function": {
                        "name": name,
                        "arguments": args
                    }
                })
            except json.JSONDecodeError:
                continue

        # Remove tool call text from content
        cleaned = re.sub(pattern, '', content).strip()
        return cleaned, tool_calls

    async def health_check(self) -> bool:
        """Check of Ollama beschikbaar is."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def get_models(self) -> Optional[list[str]]:
        """Haal beschikbare modellen op."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.url}/api/tags")
                resp.raise_for_status()
                result = resp.json()
                return [m["name"] for m in result.get("models", [])]
        except Exception:
            return None
