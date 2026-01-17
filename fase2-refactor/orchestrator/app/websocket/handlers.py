"""WebSocket message handlers."""
import asyncio
import base64
import json
import time
import uuid
from typing import Optional

from .protocol import (
    MessageType,
    Message,
    ResponseMessage,
    AudioChunkMessage,
    FunctionCallMessage,
    FunctionRequestMessage,
    ErrorMessage,
)
from .manager import ConnectionManager
from ..config import get_config
from ..models import EmotionManager, ConversationManager, FunctionCall
from ..services import OllamaLLM, VoxtralSTT, FishAudioTTS, ToolRegistry
from ..utils import split_into_sentences, ConversationDebugger

# Timeout voor remote tool execution (seconden)
REMOTE_TOOL_TIMEOUT = 30.0


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
        tool_registry: ToolRegistry,
        debugger: Optional[ConversationDebugger] = None
    ):
        self.connections = connection_manager
        self.emotions = emotion_manager
        self.conversations = conversation_manager
        self.tools = tool_registry

        # Debug logger (optioneel, via config)
        self.debugger = debugger or ConversationDebugger(enabled=False)

        # Pending remote tool requests: request_id -> (event, result_dict)
        self._pending_requests: dict[str, tuple[asyncio.Event, dict]] = {}

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
            MessageType.FUNCTION_RESULT: self._handle_function_result,
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

        # Start debug turn
        turn_id = uuid.uuid4().hex[:8]
        self.debugger.start_turn(turn_id, client_id)

        audio_b64 = message.payload.get("audio_base64")
        if not audio_b64:
            await self._send_error(client_id, conv_id, "No audio data")
            return

        try:
            # Decode audio
            audio_bytes = base64.b64decode(audio_b64)

            # === STT ===
            t0 = time.perf_counter()
            stt = VoxtralSTT(
                url=config.voxtral.url,
                model=config.voxtral.model,
                temperature=config.voxtral.temperature
            )
            user_text = await stt.transcribe(
                audio_bytes,
                language=message.payload.get("language", "nl")
            )
            stt_ms = (time.perf_counter() - t0) * 1000
            self.debugger.log_step("STT", stt_ms, {"text": user_text[:80] if user_text else ""})

            if not user_text.strip():
                await self._send_error(client_id, conv_id, "Empty transcription")
                self.debugger.end_turn()
                return

            # === LLM ===
            t0 = time.perf_counter()
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
            llm_ms = (time.perf_counter() - t0) * 1000
            self.debugger.log_step("LLM", llm_ms, {
                "response": content[:80] if content else "",
                "tool_calls": len(response.tool_calls or [])
            })

            # Process tool calls
            if response.tool_calls:
                t0 = time.perf_counter()
                content, function_calls = await self._process_tool_calls(
                    llm, messages, response.tool_calls, conv_id, client_id
                )
                tools_ms = (time.perf_counter() - t0) * 1000
                tool_details = [f"{fc.name}({fc.arguments})" for fc in function_calls]
                self.debugger.log_step("Tools", tools_ms, {"executed": ", ".join(tool_details)})
                # Log final response after tool processing
                self.debugger.log_step("LLM (final)", 0, {"response": content})

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
                t0 = time.perf_counter()
                tts = FishAudioTTS(
                    url=config.tts.url,
                    reference_id=config.tts.reference_id,
                    temperature=config.tts.temperature,
                    top_p=config.tts.top_p,
                    format=config.tts.format
                )

                tts_chunks = 0
                if config.tts.streaming:
                    # Stream per sentence
                    sentences = split_into_sentences(content)
                    for i, sentence in enumerate(sentences):
                        result = await tts.synthesize(sentence)
                        if result.audio_bytes:
                            tts_chunks += 1
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
                        tts_chunks = 1
                        audio_b64 = base64.b64encode(result.audio_bytes).decode("utf-8")
                        chunk_msg = AudioChunkMessage.create(
                            audio_base64=audio_b64,
                            conversation_id=conv_id,
                            sentence=content,
                            index=0,
                            is_last=True
                        )
                        await self.connections.send_json(client_id, chunk_msg.to_dict())

                tts_ms = (time.perf_counter() - t0) * 1000
                self.debugger.log_step("TTS", tts_ms, {"chunks": tts_chunks})

            # End debug turn
            self.debugger.end_turn()

        except Exception as e:
            self.debugger.end_turn()
            await self._send_error(client_id, conv_id, f"Processing error: {str(e)}")

    async def _process_tool_calls(
        self,
        llm: OllamaLLM,
        messages: list[dict],
        tool_calls: list[dict],
        conv_id: str,
        client_id: str
    ) -> tuple[str, list[FunctionCall]]:
        """
        Process tool calls recursief.

        Remote tools (is_remote=True) worden naar de Pi gestuurd.
        Zie D016 in DECISIONS.md.
        """
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

            # Check of tool remote is
            tool = self.tools.get(name)
            is_remote = getattr(tool, 'is_remote', False) if tool else False

            if is_remote:
                # Remote tool: stuur naar Pi en wacht op resultaat
                result, context = await self._execute_remote_tool(
                    client_id, conv_id, name, args
                )
                # Voor vision tools: voer analyse uit met de ontvangen image
                if tool and context.get("image_base64"):
                    result = await tool.execute(args, context)
            else:
                # Lokale tool: direct uitvoeren
                result = await self.tools.execute(name, args)

            messages.append({"role": "tool", "content": result})

        # Get final response
        response = await llm.chat(messages=messages, tools=None)

        if response.tool_calls:
            more_content, more_calls = await self._process_tool_calls(
                llm, messages, response.tool_calls, conv_id, client_id
            )
            return more_content, all_calls + more_calls

        return response.content, all_calls

    async def _execute_remote_tool(
        self,
        client_id: str,
        conv_id: str,
        name: str,
        args: dict
    ) -> tuple[str, dict]:
        """
        Voer remote tool uit op Pi.

        1. Stuur FUNCTION_REQUEST naar Pi
        2. Wacht op FUNCTION_RESULT
        3. Return result en context (evt. met image_base64)
        """
        request_id = str(uuid.uuid4())

        # Maak event om op te wachten
        event = asyncio.Event()
        result_holder: dict = {}
        self._pending_requests[request_id] = (event, result_holder)

        try:
            # Stuur request naar Pi
            request_msg = FunctionRequestMessage.create(
                name=name,
                arguments=args,
                request_id=request_id,
                conversation_id=conv_id
            )
            await self.connections.send_json(client_id, request_msg.to_dict())

            # Wacht op result met timeout
            try:
                await asyncio.wait_for(event.wait(), timeout=REMOTE_TOOL_TIMEOUT)
            except asyncio.TimeoutError:
                return f"Remote tool '{name}' timeout na {REMOTE_TOOL_TIMEOUT}s", {}

            # Haal resultaat op
            result = result_holder.get("result", "")
            context = {}
            if result_holder.get("image_base64"):
                context["image_base64"] = result_holder["image_base64"]
            if result_holder.get("error"):
                result = f"Remote tool error: {result_holder['error']}"

            return result, context

        finally:
            # Cleanup
            self._pending_requests.pop(request_id, None)

    async def _handle_function_result(self, client_id: str, message: Message) -> None:
        """
        Handle FUNCTION_RESULT van Pi.

        Unblocks de wachtende _execute_remote_tool call.
        """
        payload = message.payload
        request_id = payload.get("request_id", "")

        if request_id not in self._pending_requests:
            # Onbekende request_id - negeer (misschien al getimed out)
            return

        event, result_holder = self._pending_requests[request_id]

        # Kopieer resultaat
        result_holder["result"] = payload.get("result", "")
        if payload.get("image_base64"):
            result_holder["image_base64"] = payload["image_base64"]
        if payload.get("error"):
            result_holder["error"] = payload["error"]

        # Signal dat resultaat binnen is
        event.set()

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
