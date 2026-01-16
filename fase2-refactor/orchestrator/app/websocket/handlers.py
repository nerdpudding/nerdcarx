"""WebSocket message handlers."""
import base64
import json
from typing import Optional

from .protocol import (
    MessageType,
    Message,
    ResponseMessage,
    AudioChunkMessage,
    FunctionCallMessage,
    ErrorMessage,
)
from .manager import ConnectionManager
from ..config import get_config
from ..models import EmotionManager, ConversationManager, FunctionCall
from ..services import OllamaLLM, VoxtralSTT, FishAudioTTS, ToolRegistry
from ..utils import split_into_sentences


class MessageHandler:
    """
    Handler voor WebSocket messages.

    Verwerkt binnenkomende messages en stuurt responses.
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        emotion_manager: EmotionManager,
        conversation_manager: ConversationManager,
        tool_registry: ToolRegistry
    ):
        self.connections = connection_manager
        self.emotions = emotion_manager
        self.conversations = conversation_manager
        self.tools = tool_registry

    async def handle_message(self, client_id: str, raw_data: str) -> None:
        """
        Verwerk binnenkomend message.

        Args:
            client_id: Client identifier
            raw_data: Raw JSON string
        """
        try:
            data = json.loads(raw_data)
            message = Message.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            await self._send_error(client_id, "default", f"Invalid message: {e}")
            return

        # Update heartbeat voor alle messages
        self.connections.update_heartbeat(client_id)

        # Route naar juiste handler
        handlers = {
            MessageType.AUDIO_PROCESS: self._handle_audio_process,
            MessageType.WAKE_WORD: self._handle_wake_word,
            MessageType.SENSOR_UPDATE: self._handle_sensor_update,
            MessageType.HEARTBEAT: self._handle_heartbeat,
        }

        handler = handlers.get(message.type)
        if handler:
            await handler(client_id, message)
        else:
            await self._send_error(
                client_id,
                message.conversation_id,
                f"Unknown message type: {message.type}"
            )

    async def _handle_audio_process(self, client_id: str, message: Message) -> None:
        """
        Verwerk audio: STT → LLM → TTS → Response.

        Flow:
        1. Transcribeer audio naar tekst (STT)
        2. Stuur naar LLM met tools
        3. Verwerk tool calls
        4. Genereer TTS audio
        5. Stuur response en audio chunks
        """
        config = get_config()
        conv_id = message.conversation_id

        audio_b64 = message.payload.get("audio_base64")
        if not audio_b64:
            await self._send_error(client_id, conv_id, "No audio data")
            return

        try:
            # Decode audio
            audio_bytes = base64.b64decode(audio_b64)

            # === STT ===
            stt = VoxtralSTT(
                url=config.voxtral.url,
                model=config.voxtral.model,
                temperature=config.voxtral.temperature
            )
            user_text = await stt.transcribe(
                audio_bytes,
                language=message.payload.get("language", "nl")
            )

            if not user_text.strip():
                await self._send_error(client_id, conv_id, "Empty transcription")
                return

            # === LLM ===
            llm = OllamaLLM(
                url=config.ollama.url,
                model=config.ollama.model,
                temperature=config.ollama.temperature,
                top_p=config.ollama.top_p,
                repeat_penalty=config.ollama.repeat_penalty,
                num_ctx=config.ollama.num_ctx
            )

            # Get emotion state
            emotion_state = self.emotions.get_state(conv_id)
            current_emotion = emotion_state.emotion

            # Build system prompt with emotion
            emotion_context = f"\n\nJe huidige emotionele staat is: {current_emotion}."
            system_prompt = config.system_prompt + emotion_context

            # Get or create conversation
            conv = self.conversations.get_or_create(conv_id, config.system_prompt)
            conv.add_user_message(user_text)

            messages = conv.to_ollama_messages(system_prompt)
            tools = self.tools.get_definitions()

            response = await llm.chat(messages=messages, tools=tools)
            content = response.content
            function_calls = []

            # Process tool calls
            if response.tool_calls:
                content, function_calls = await self._process_tool_calls(
                    llm, messages, response.tool_calls, conv_id
                )

            conv.add_assistant_message(content)

            # Check emotion changes
            new_emotion = current_emotion
            for fc in function_calls:
                if fc.name == "show_emotion":
                    new_emotion = fc.arguments.get("emotion", current_emotion)
                    self.emotions.update_emotion(conv_id, new_emotion)

            # Send function calls to Pi
            for fc in function_calls:
                fc_msg = FunctionCallMessage.create(
                    name=fc.name,
                    arguments=fc.arguments,
                    conversation_id=conv_id
                )
                await self.connections.send_json(client_id, fc_msg.to_dict())

            # Send text response
            response_msg = ResponseMessage.create(
                text=content,
                conversation_id=conv_id,
                emotion=new_emotion,
                function_calls=[{"name": fc.name, "arguments": fc.arguments} for fc in function_calls]
            )
            await self.connections.send_json(client_id, response_msg.to_dict())

            # === TTS ===
            if config.tts.enabled and content.strip():
                tts = FishAudioTTS(
                    url=config.tts.url,
                    reference_id=config.tts.reference_id,
                    temperature=config.tts.temperature,
                    top_p=config.tts.top_p,
                    format=config.tts.format
                )

                if config.tts.streaming:
                    # Stream per sentence
                    sentences = split_into_sentences(content)
                    for i, sentence in enumerate(sentences):
                        result = await tts.synthesize(sentence)
                        if result.audio_bytes:
                            audio_b64 = base64.b64encode(result.audio_bytes).decode("utf-8")
                            chunk_msg = AudioChunkMessage.create(
                                audio_base64=audio_b64,
                                conversation_id=conv_id,
                                sentence=sentence,
                                index=i,
                                is_last=(i == len(sentences) - 1)
                            )
                            await self.connections.send_json(client_id, chunk_msg.to_dict())
                else:
                    # Single audio response
                    result = await tts.synthesize(content)
                    if result.audio_bytes:
                        audio_b64 = base64.b64encode(result.audio_bytes).decode("utf-8")
                        chunk_msg = AudioChunkMessage.create(
                            audio_base64=audio_b64,
                            conversation_id=conv_id,
                            sentence=content,
                            index=0,
                            is_last=True
                        )
                        await self.connections.send_json(client_id, chunk_msg.to_dict())

        except Exception as e:
            await self._send_error(client_id, conv_id, f"Processing error: {str(e)}")

    async def _process_tool_calls(
        self,
        llm: OllamaLLM,
        messages: list[dict],
        tool_calls: list[dict],
        conv_id: str
    ) -> tuple[str, list[FunctionCall]]:
        """Process tool calls recursief."""
        all_calls = []

        messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": tool_calls
        })

        for tc in tool_calls:
            func = tc.get("function", {})
            name = func.get("name", "")
            args = func.get("arguments", {})

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}

            all_calls.append(FunctionCall(name=name, arguments=args))

            result = await self.tools.execute(name, args)
            messages.append({"role": "tool", "content": result})

        # Get final response
        response = await llm.chat(messages=messages, tools=None)

        if response.tool_calls:
            more_content, more_calls = await self._process_tool_calls(
                llm, messages, response.tool_calls, conv_id
            )
            return more_content, all_calls + more_calls

        return response.content, all_calls

    async def _handle_wake_word(self, client_id: str, message: Message) -> None:
        """Handle wake word detection."""
        # Voor nu: log het en bevestig
        # Later: kan UI update triggeren of conversation resetten
        pass

    async def _handle_sensor_update(self, client_id: str, message: Message) -> None:
        """Handle sensor data update."""
        # Voor nu: log het
        # Later: kan gebruikt worden voor context-aware responses
        pass

    async def _handle_heartbeat(self, client_id: str, message: Message) -> None:
        """Handle heartbeat - already updated in handle_message."""
        pass

    async def _send_error(self, client_id: str, conv_id: str, error: str) -> None:
        """Stuur error message naar client."""
        error_msg = ErrorMessage.create(error=error, conversation_id=conv_id)
        await self.connections.send_json(client_id, error_msg.to_dict())
