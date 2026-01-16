"""LLM Provider protocol."""
from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable


@dataclass
class LLMResponse:
    """Response van een LLM call."""
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    model: str = ""
    done: bool = True


@runtime_checkable
class LLMProvider(Protocol):
    """
    Protocol voor LLM providers.

    Implementaties:
    - OllamaLLM (Ollama met Ministral)
    - Toekomst: OpenAILLM, AnthropicLLM, etc.
    """

    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        temperature: Optional[float] = None,
        num_ctx: Optional[int] = None
    ) -> LLMResponse:
        """
        Stuur messages naar LLM en krijg response.

        Args:
            messages: Lijst van messages in Ollama format
            tools: Optionele tool definitions
            temperature: Optionele temperature override
            num_ctx: Optionele context window override

        Returns:
            LLMResponse met content en optionele tool calls
        """
        ...

    async def health_check(self) -> bool:
        """Check of de LLM service beschikbaar is."""
        ...
