"""
Conversation debug logging.

Logt conversation turns met timing en details naar console en optioneel naar file.
"""
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class ConversationDebugger:
    """
    Logt conversation turns met timing en details.

    Usage:
        debugger = ConversationDebugger(enabled=True, log_file="logs/conv.log")
        debugger.start_turn("abc123", "pi-client")
        debugger.log_step("STT", 450.0, {"text": "hallo daar"})
        debugger.log_step("LLM", 1200.0, {"response": "Hoi!", "tools": 0})
        debugger.end_turn()
    """

    def __init__(
        self,
        enabled: bool = False,
        log_file: Optional[str] = None,
        verbose: bool = False
    ):
        self.enabled = enabled
        self.verbose = verbose
        self.log_file = None

        if log_file and enabled:
            self.log_file = Path(log_file)
            # Maak parent directory aan indien nodig
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.current_turn: dict = {}

    def start_turn(self, turn_id: str, client_id: str) -> None:
        """Start een nieuwe turn."""
        if not self.enabled:
            return

        self.current_turn = {
            "turn_id": turn_id,
            "client_id": client_id,
            "started_at": time.time(),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "steps": []
        }

    def log_step(
        self,
        step: str,
        duration_ms: float,
        details: Optional[dict] = None
    ) -> None:
        """Log een stap binnen de huidige turn."""
        if not self.enabled or not self.current_turn:
            return

        self.current_turn["steps"].append({
            "step": step,
            "duration_ms": duration_ms,
            "details": details or {}
        })

    def end_turn(self) -> None:
        """Beëindig turn en schrijf output."""
        if not self.enabled or not self.current_turn:
            return

        # Bereken totale tijd
        total_ms = (time.time() - self.current_turn["started_at"]) * 1000
        self.current_turn["total_ms"] = total_ms

        output = self._format_turn(self.current_turn)
        print(output)

        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(output + "\n")

        self.current_turn = {}

    def _format_turn(self, turn: dict) -> str:
        """Format turn data als leesbare string."""
        lines = [
            f"\n{'─' * 60}",
            f"[{turn['timestamp']}] Turn {turn['turn_id']} | Client: {turn['client_id']}",
            f"{'─' * 60}",
        ]

        for step in turn["steps"]:
            step_name = step["step"]
            duration = step["duration_ms"]
            lines.append(f"  {step_name}: {duration:.0f}ms")

            # Verbose details
            if self.verbose and step.get("details"):
                for key, value in step["details"].items():
                    # Truncate lange waarden
                    if isinstance(value, str) and len(value) > 60:
                        value = value[:57] + "..."
                    lines.append(f"    └─ {key}: {value}")

        # Totaal
        lines.append(f"{'─' * 40}")
        lines.append(f"  TOTAL: {turn.get('total_ms', 0):.0f}ms")
        lines.append(f"{'─' * 60}")

        return "\n".join(lines)
