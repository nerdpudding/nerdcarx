"""Sleep tool - laat robot terug naar wake word mode gaan."""
from typing import Optional


class SleepTool:
    """
    go_to_sleep tool - beëindigt conversatie en gaat terug naar wake word.

    Dit is een remote tool - de Pi client handelt dit af door
    de conversation loop te stoppen en terug te gaan naar wake word detectie.
    """

    @property
    def name(self) -> str:
        return "go_to_sleep"

    @property
    def is_remote(self) -> bool:
        return True

    @property
    def definition(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "go_to_sleep",
                "description": "Ga naar slaapstand. Roep DIRECT aan als de gebruiker 'go to sleep' zegt.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

    async def execute(self, arguments: dict, context: Optional[dict] = None) -> str:
        """Execute sleep tool - actual action gebeurt op Pi."""
        return "Oké, ik ga slapen. Zeg 'hey Jarvis' als je me weer nodig hebt."
