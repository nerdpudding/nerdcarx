"""WebSocket support voor Pi ↔ Desktop communicatie."""
from .protocol import MessageType, Message, AudioProcessMessage, ResponseMessage
from .manager import ConnectionManager
from .handlers import MessageHandler

__all__ = [
    "MessageType",
    "Message",
    "AudioProcessMessage",
    "ResponseMessage",
    "ConnectionManager",
    "MessageHandler",
]
