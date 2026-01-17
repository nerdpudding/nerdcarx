"""Tool protocol en registry."""
from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """
    Protocol voor LLM tools.

    Elke tool heeft:
    - name: Unieke identifier
    - definition: OpenAI-compatible tool definition
    - is_remote: Of tool op Pi moet draaien (default: False)
    - execute: Async execution method

    Remote tools (is_remote=True) worden via WebSocket naar de Pi gestuurd.
    Zie D016 in DECISIONS.md voor rationale.
    """

    @property
    def name(self) -> str:
        """Unieke tool naam."""
        ...

    @property
    def definition(self) -> dict:
        """
        OpenAI-compatible tool definition.

        Format:
        {
            "type": "function",
            "function": {
                "name": "...",
                "description": "...",
                "parameters": {...}
            }
        }
        """
        ...

    @property
    def is_remote(self) -> bool:
        """
        True als tool op de Pi moet worden uitgevoerd.

        Remote tools:
        - take_photo: Camera zit op Pi
        - show_emotion: OLED zit op Pi
        - drive, set_leds: Hardware op Pi

        Local tools (default):
        - web_search: Internet via Desktop
        - MCP tools: Desktop integraties
        """
        return False  # Default: lokaal uitvoeren

    async def execute(self, arguments: dict, context: Optional[dict] = None) -> str:
        """
        Voer tool uit.

        Args:
            arguments: Tool arguments van LLM
            context: Optionele execution context

        Returns:
            Tool result als string
        """
        ...


class ToolRegistry:
    """
    Registry voor beschikbare tools.

    Beheert tool registratie en lookup.
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Registreer een tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Haal tool op bij naam."""
        return self._tools.get(name)

    def get_definitions(self) -> list[dict]:
        """Haal alle tool definitions op (voor LLM)."""
        return [tool.definition for tool in self._tools.values()]

    def list_names(self) -> list[str]:
        """Lijst alle tool namen."""
        return list(self._tools.keys())

    async def execute(
        self,
        name: str,
        arguments: dict,
        context: Optional[dict] = None
    ) -> str:
        """
        Voer tool uit bij naam.

        Args:
            name: Tool naam
            arguments: Tool arguments
            context: Execution context

        Returns:
            Tool result of error message
        """
        tool = self.get(name)
        if tool is None:
            return f"Onbekende tool: {name}"
        return await tool.execute(arguments, context)
