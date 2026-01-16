"""Emotion tool voor robot display."""
from typing import Optional


class EmotionTool:
    """
    show_emotion tool - toont emotie op robot OLED display.

    Dit is een "fire and forget" tool - de actual display update
    gebeurt door de Pi client op basis van function_calls in de response.
    """

    def __init__(self, available_emotions: Optional[list[str]] = None):
        self.available_emotions = available_emotions or [
            "happy", "sad", "angry", "surprised", "neutral",
            "curious", "confused", "excited", "thinking", "shy",
            "love", "tired", "bored", "proud", "worried"
        ]

    @property
    def name(self) -> str:
        return "show_emotion"

    @property
    def definition(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "show_emotion",
                "description": "Toon een emotie op het OLED display van de robot. Gebruik alleen bij duidelijke emotionele context.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "emotion": {
                            "type": "string",
                            "enum": self.available_emotions,
                            "description": "De emotie om te tonen"
                        }
                    },
                    "required": ["emotion"]
                }
            }
        }

    async def execute(self, arguments: dict, context: Optional[dict] = None) -> str:
        """
        Execute emotion tool.

        Note: De actual display update wordt gedaan door de client.
        Deze functie is alleen voor de LLM conversation flow.
        """
        emotion = arguments.get("emotion", "neutral")

        if emotion not in self.available_emotions:
            return f"Onbekende emotie: {emotion}. Beschikbaar: {', '.join(self.available_emotions)}"

        return f"Emotie '{emotion}' wordt getoond op het display."
