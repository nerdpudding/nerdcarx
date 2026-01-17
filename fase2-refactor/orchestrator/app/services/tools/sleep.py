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
                "description": "Beëindig de conversatie en ga naar slaapstand. De robot stopt met luisteren totdat het wake word opnieuw wordt gezegd. Gebruik wanneer de gebruiker aangeeft klaar te zijn, of vraagt om te stoppen met luisteren.",
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
