"""WebSocket protocol definitions."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import time


class MessageType(str, Enum):
    """WebSocket message types."""

    # Pi → Desktop
    AUDIO_PROCESS = "audio_process"     # Audio voor transcriptie + LLM
    WAKE_WORD = "wake_word"             # Wake word gedetecteerd
    SENSOR_UPDATE = "sensor_update"     # Sensor data
    HEARTBEAT = "heartbeat"             # Keep-alive

    # Desktop → Pi
    RESPONSE = "response"               # LLM response tekst
    AUDIO_CHUNK = "audio_chunk"         # TTS audio chunk
    FUNCTION_CALL = "function_call"     # Tool execution request
    ERROR = "error"                     # Foutmelding


@dataclass
class Message:
    """Base WebSocket message."""
    type: MessageType
    conversation_id: str
    timestamp: float = field(default_factory=time.time)
    payload: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            type=MessageType(data["type"]),
            conversation_id=data.get("conversation_id", "default"),
            timestamp=data.get("timestamp", time.time()),
            payload=data.get("payload", {})
        )


@dataclass
class AudioProcessMessage(Message):
    """Audio processing request van Pi."""
    type: MessageType = field(default=MessageType.AUDIO_PROCESS, init=False)

    @property
    def audio_base64(self) -> Optional[str]:
        return self.payload.get("audio_base64")

    @property
    def language(self) -> str:
        return self.payload.get("language", "nl")

    @classmethod
    def create(
        cls,
        audio_base64: str,
        conversation_id: str = "default",
        language: str = "nl"
    ) -> "AudioProcessMessage":
        return cls(
            conversation_id=conversation_id,
            payload={"audio_base64": audio_base64, "language": language}
        )


@dataclass
class WakeWordMessage(Message):
    """Wake word detection notification."""
    type: MessageType = field(default=MessageType.WAKE_WORD, init=False)

    @classmethod
    def create(cls, conversation_id: str = "default") -> "WakeWordMessage":
        return cls(conversation_id=conversation_id)


@dataclass
class HeartbeatMessage(Message):
    """Heartbeat/keep-alive message."""
    type: MessageType = field(default=MessageType.HEARTBEAT, init=False)

    @classmethod
    def create(cls, conversation_id: str = "default") -> "HeartbeatMessage":
        return cls(conversation_id=conversation_id)


@dataclass
class ResponseMessage(Message):
    """LLM response naar Pi."""
    type: MessageType = field(default=MessageType.RESPONSE, init=False)

    @classmethod
    def create(
        cls,
        text: str,
        conversation_id: str = "default",
        emotion: Optional[str] = None,
        function_calls: Optional[list[dict]] = None
    ) -> "ResponseMessage":
        payload = {"text": text}
        if emotion:
            payload["emotion"] = emotion
        if function_calls:
            payload["function_calls"] = function_calls
        return cls(conversation_id=conversation_id, payload=payload)


@dataclass
class AudioChunkMessage(Message):
    """TTS audio chunk naar Pi."""
    type: MessageType = field(default=MessageType.AUDIO_CHUNK, init=False)

    @classmethod
    def create(
        cls,
        audio_base64: str,
        conversation_id: str = "default",
        sentence: Optional[str] = None,
        index: int = 0,
        is_last: bool = False
    ) -> "AudioChunkMessage":
        return cls(
            conversation_id=conversation_id,
            payload={
                "audio_base64": audio_base64,
                "sentence": sentence,
                "index": index,
                "is_last": is_last
            }
        )


@dataclass
class FunctionCallMessage(Message):
    """Function call request naar Pi."""
    type: MessageType = field(default=MessageType.FUNCTION_CALL, init=False)

    @classmethod
    def create(
        cls,
        name: str,
        arguments: dict,
        conversation_id: str = "default"
    ) -> "FunctionCallMessage":
        return cls(
            conversation_id=conversation_id,
            payload={"name": name, "arguments": arguments}
        )


@dataclass
class ErrorMessage(Message):
    """Error message naar Pi."""
    type: MessageType = field(default=MessageType.ERROR, init=False)

    @classmethod
    def create(
        cls,
        error: str,
        conversation_id: str = "default",
        code: Optional[str] = None
    ) -> "ErrorMessage":
        payload = {"error": error}
        if code:
            payload["code"] = code
        return cls(conversation_id=conversation_id, payload=payload)
