"""WebSocket endpoint."""
import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from ..config import get_config
from ..models import EmotionManager, ConversationManager
from ..services.tools import ToolRegistry, EmotionTool, VisionTool
from ..utils import ConversationDebugger
from ..websocket import ConnectionManager, MessageHandler

router = APIRouter(tags=["websocket"])

# Global instances
_connection_manager: Optional[ConnectionManager] = None
_message_handler: Optional[MessageHandler] = None


def get_connection_manager() -> ConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        config = get_config()
        _connection_manager = ConnectionManager(
            heartbeat_timeout=config.websocket.heartbeat_interval * 2
        )
    return _connection_manager


def get_message_handler() -> MessageHandler:
    global _message_handler
    if _message_handler is None:
        config = get_config()

        emotion_manager = EmotionManager(
            default_emotion=config.emotions.default,
            auto_reset_minutes=config.emotions.auto_reset_minutes,
            available_emotions=config.emotions.available
        )

        conversation_manager = ConversationManager(
            default_system_prompt=config.system_prompt
        )

        tool_registry = ToolRegistry()
        tool_registry.register(EmotionTool(available_emotions=config.emotions.available))
        tool_registry.register(VisionTool(
            mock_image_path=config.vision.mock_image_path,
            pi_camera_url=config.vision.pi_camera_url,
            llm_url=config.ollama.url,
            llm_model=config.ollama.model
        ))

        # Debug logger (config bepaalt of het actief is)
        debugger = ConversationDebugger(
            enabled=config.debug.enabled,
            log_file=config.debug.log_file,
            verbose=config.debug.verbose
        )

        _message_handler = MessageHandler(
            connection_manager=get_connection_manager(),
            emotion_manager=emotion_manager,
            conversation_manager=conversation_manager,
            tool_registry=tool_registry,
            debugger=debugger
        )
    return _message_handler


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(default=None),
    conversation_id: str = Query(default="default")
):
    """
    WebSocket endpoint voor Pi ↔ Desktop communicatie.

    Query parameters:
        client_id: Unieke client identifier (optioneel, auto-generated)
        conversation_id: Conversation ID (default: "default")

    Message format (JSON):
        {
            "type": "audio_process|wake_word|heartbeat|sensor_update",
            "conversation_id": "default",
            "timestamp": 1234567890.123,
            "payload": {...}
        }
    """
    config = get_config()

    if not config.websocket.enabled:
        await websocket.close(code=1008, reason="WebSocket disabled")
        return

    connection_manager = get_connection_manager()
    message_handler = get_message_handler()

    # Generate client ID if not provided
    if not client_id:
        client_id = f"pi-{uuid.uuid4().hex[:8]}"

    # Connect
    connection = await connection_manager.connect(
        websocket=websocket,
        client_id=client_id,
        conversation_id=conversation_id
    )

    try:
        # Gebruik een queue om berichten te bufferen
        # Dit voorkomt deadlock bij remote tool calls (D016)
        message_queue: asyncio.Queue = asyncio.Queue()

        async def receive_loop():
            """Ontvangt berichten en zet ze in de queue."""
            try:
                while True:
                    data = await websocket.receive_text()
                    await message_queue.put(data)
            except WebSocketDisconnect:
                await message_queue.put(None)  # Signal to stop

        async def process_loop():
            """Verwerkt berichten uit de queue."""
            while True:
                data = await message_queue.get()
                if data is None:
                    break
                # Spawn message handling als aparte task
                # zodat we direct door kunnen met ontvangen
                asyncio.create_task(
                    message_handler.handle_message(client_id, data)
                )

        # Run receive en process parallel
        receive_task = asyncio.create_task(receive_loop())
        process_task = asyncio.create_task(process_loop())

        # Wacht tot een van beide stopt
        done, pending = await asyncio.wait(
            [receive_task, process_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(client_id)


@router.get("/ws/clients")
async def list_websocket_clients():
    """Toon actieve WebSocket clients."""
    connection_manager = get_connection_manager()
    return {
        "active_count": connection_manager.active_count,
        "clients": connection_manager.list_clients()
    }
