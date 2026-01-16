"""Chat en conversation endpoints."""
import json
import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx

from ..config import get_config
from ..models import (
    ChatRequest,
    ChatResponse,
    FunctionCall,
    EmotionInfo,
    EmotionManager,
    ConversationManager,
)
from ..services import OllamaLLM, FishAudioTTS, ToolRegistry, EmotionTool, VisionTool
from ..utils import split_into_sentences

router = APIRouter(tags=["chat"])

# Global managers (initialized at startup)
_emotion_manager: Optional[EmotionManager] = None
_conversation_manager: Optional[ConversationManager] = None
_tool_registry: Optional[ToolRegistry] = None


def get_emotion_manager() -> EmotionManager:
    global _emotion_manager
    if _emotion_manager is None:
        config = get_config()
        _emotion_manager = EmotionManager(
            default_emotion=config.emotions.default,
            auto_reset_minutes=config.emotions.auto_reset_minutes,
            available_emotions=config.emotions.available
        )
    return _emotion_manager


def get_conversation_manager() -> ConversationManager:
    global _conversation_manager
    if _conversation_manager is None:
        config = get_config()
        _conversation_manager = ConversationManager(
            default_system_prompt=config.system_prompt
        )
    return _conversation_manager


def get_tool_registry() -> ToolRegistry:
    global _tool_registry
    if _tool_registry is None:
        config = get_config()
        _tool_registry = ToolRegistry()
        _tool_registry.register(EmotionTool(available_emotions=config.emotions.available))
        _tool_registry.register(VisionTool(
            mock_image_path=config.vision.mock_image_path,
            pi_camera_url=config.vision.pi_camera_url,
            llm_url=config.ollama.url,
            llm_model=config.ollama.model
        ))
    return _tool_registry


async def complete_tool_calls(
    llm: OllamaLLM,
    messages: list[dict],
    tool_calls: list[dict],
    tool_registry: ToolRegistry,
    options: dict
) -> tuple[str, list[FunctionCall]]:
    """
    Voer tool calls uit en krijg finale response.

    Returns: (content, all_function_calls)
    """
    all_function_calls = []

    # Voeg assistant message met tool calls toe
    messages.append({
        "role": "assistant",
        "content": "",
        "tool_calls": tool_calls
    })

    # Voer elke tool call uit
    for tc in tool_calls:
        func = tc.get("function", {})
        name = func.get("name", "")
        args = func.get("arguments", {})

        # Parse arguments als string
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}

        all_function_calls.append(FunctionCall(name=name, arguments=args))

        # Voer tool uit
        tool_result = await tool_registry.execute(name, args)

        messages.append({
            "role": "tool",
            "content": tool_result
        })

    # Vraag om finale response (zonder tools)
    response = await llm.chat(
        messages=messages,
        tools=None,
        temperature=options.get("temperature"),
        num_ctx=options.get("num_ctx")
    )

    content = response.content

    # Check voor meer tool calls (recursief)
    if response.tool_calls:
        more_content, more_calls = await complete_tool_calls(
            llm, messages, response.tool_calls, tool_registry, options
        )
        content = more_content
        all_function_calls.extend(more_calls)

    return content, all_function_calls


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Stuur een bericht naar de LLM (stateless).
    """
    config = get_config()
    tool_registry = get_tool_registry()

    system_prompt = request.system_prompt or config.system_prompt
    temperature = request.temperature or config.ollama.temperature
    num_ctx = request.num_ctx or config.ollama.num_ctx

    # Build user message
    user_message = {"role": "user", "content": request.message}
    if request.image_base64:
        user_message["images"] = [request.image_base64]

    messages = [
        {"role": "system", "content": system_prompt},
        user_message
    ]

    # Get tools if enabled
    tools = tool_registry.get_definitions() if request.enable_tools else None

    llm = OllamaLLM(
        url=config.ollama.url,
        model=config.ollama.model,
        temperature=config.ollama.temperature,
        top_p=config.ollama.top_p,
        repeat_penalty=config.ollama.repeat_penalty,
        num_ctx=config.ollama.num_ctx
    )

    try:
        response = await llm.chat(
            messages=messages,
            tools=tools,
            temperature=temperature,
            num_ctx=num_ctx
        )

        function_calls = []
        content = response.content

        if response.tool_calls:
            content, function_calls = await complete_tool_calls(
                llm, messages, response.tool_calls, tool_registry,
                {"temperature": temperature, "num_ctx": num_ctx}
            )

        return ChatResponse(
            response=content,
            model=config.ollama.model,
            conversation_id=request.conversation_id,
            function_calls=function_calls if function_calls else None
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama niet bereikbaar")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation", response_model=ChatResponse)
async def conversation(request: ChatRequest):
    """
    Chat met conversation history, function calling, en emotion state.
    """
    config = get_config()
    emotion_manager = get_emotion_manager()
    conversation_manager = get_conversation_manager()
    tool_registry = get_tool_registry()

    conv_id = request.conversation_id or "default"
    system_prompt = request.system_prompt or config.system_prompt
    temperature = request.temperature or config.ollama.temperature
    num_ctx = request.num_ctx or config.ollama.num_ctx

    # Get emotion state (met auto-reset check)
    emotion_state = emotion_manager.get_state(conv_id)
    current_emotion = emotion_state.emotion
    was_auto_reset = emotion_state.auto_reset

    # Voeg emotie context toe aan system prompt
    emotion_context = f"\n\nJe huidige emotionele staat is: {current_emotion}. Verander deze alleen als de interactie daar aanleiding toe geeft."
    enhanced_system_prompt = system_prompt + emotion_context

    # Get or create conversation
    conv = conversation_manager.get_or_create(conv_id, system_prompt)

    # Add user message
    conv.add_user_message(request.message)

    # Build messages voor LLM
    messages = conv.to_ollama_messages(enhanced_system_prompt)

    # Add image to last user message if present
    if request.image_base64:
        messages[-1]["images"] = [request.image_base64]

    # Get tools
    tools = tool_registry.get_definitions() if request.enable_tools is not False else None

    llm = OllamaLLM(
        url=config.ollama.url,
        model=config.ollama.model,
        temperature=config.ollama.temperature,
        top_p=config.ollama.top_p,
        repeat_penalty=config.ollama.repeat_penalty,
        num_ctx=config.ollama.num_ctx
    )

    try:
        # === TIMING: LLM START ===
        t_llm_start = time.perf_counter()

        response = await llm.chat(
            messages=messages,
            tools=tools,
            temperature=temperature,
            num_ctx=num_ctx
        )

        function_calls = []
        content = response.content

        if response.tool_calls:
            content, function_calls = await complete_tool_calls(
                llm, messages, response.tool_calls, tool_registry,
                {"temperature": temperature, "num_ctx": num_ctx}
            )

        # === TIMING: LLM END ===
        t_llm_end = time.perf_counter()
        timing_llm_ms = round((t_llm_end - t_llm_start) * 1000)

        # Check emotion changes
        emotion_changed = False
        new_emotion = current_emotion
        had_emotion_tool_call = False

        for fc in function_calls:
            if fc.name == "show_emotion":
                had_emotion_tool_call = True
                new_emotion = fc.arguments.get("emotion", current_emotion)
                if emotion_manager.update_emotion(conv_id, new_emotion):
                    emotion_changed = True

        # Add assistant response to history
        conv.add_assistant_message(content)

        # === TIMING: TTS START ===
        t_tts_start = time.perf_counter()

        # TTS synthesis
        audio_base64 = None
        normalized_text = None

        if config.tts.enabled and content.strip():
            tts = FishAudioTTS(
                url=config.tts.url,
                reference_id=config.tts.reference_id,
                temperature=config.tts.temperature,
                top_p=config.tts.top_p,
                format=config.tts.format
            )
            audio_base64, normalized_text = await tts.synthesize_base64(content)

        # === TIMING: TTS END ===
        t_tts_end = time.perf_counter()
        timing_tts_ms = round((t_tts_end - t_tts_start) * 1000)

        return ChatResponse(
            response=content,
            model=config.ollama.model,
            conversation_id=conv_id,
            function_calls=function_calls if function_calls else None,
            emotion=EmotionInfo(
                current=new_emotion,
                changed=emotion_changed,
                auto_reset=was_auto_reset,
                had_tool_call=had_emotion_tool_call
            ),
            audio_base64=audio_base64,
            timing_ms={"llm": timing_llm_ms, "tts": timing_tts_ms},
            normalized_text=normalized_text
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama niet bereikbaar")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/streaming")
async def conversation_streaming(request: ChatRequest):
    """
    Streaming conversation endpoint.
    Stuurt LLM response als tekst, gevolgd door TTS audio per zin als SSE events.
    """
    config = get_config()
    emotion_manager = get_emotion_manager()
    conversation_manager = get_conversation_manager()
    tool_registry = get_tool_registry()

    conv_id = request.conversation_id or "default"
    system_prompt = request.system_prompt or config.system_prompt
    temperature = request.temperature or config.ollama.temperature
    num_ctx = request.num_ctx or config.ollama.num_ctx

    # Get emotion state
    emotion_state = emotion_manager.get_state(conv_id)
    current_emotion = emotion_state.emotion
    was_auto_reset = emotion_state.auto_reset

    emotion_context = f"\n\nJe huidige emotionele staat is: {current_emotion}. Verander deze alleen als de interactie daar aanleiding toe geeft."
    enhanced_system_prompt = system_prompt + emotion_context

    # Get or create conversation
    conv = conversation_manager.get_or_create(conv_id, system_prompt)
    conv.add_user_message(request.message)

    messages = conv.to_ollama_messages(enhanced_system_prompt)

    tools = tool_registry.get_definitions() if request.enable_tools is not False else None

    llm = OllamaLLM(
        url=config.ollama.url,
        model=config.ollama.model,
        temperature=config.ollama.temperature,
        top_p=config.ollama.top_p,
        repeat_penalty=config.ollama.repeat_penalty,
        num_ctx=config.ollama.num_ctx
    )

    async def generate_stream():
        try:
            # LLM call
            t_llm_start = time.perf_counter()
            response = await llm.chat(
                messages=messages,
                tools=tools,
                temperature=temperature,
                num_ctx=num_ctx
            )

            function_calls = []
            content = response.content

            if response.tool_calls:
                content, function_calls = await complete_tool_calls(
                    llm, messages, response.tool_calls, tool_registry,
                    {"temperature": temperature, "num_ctx": num_ctx}
                )

            t_llm_end = time.perf_counter()
            timing_llm_ms = round((t_llm_end - t_llm_start) * 1000)

            # Check emotion changes
            emotion_changed = False
            new_emotion = current_emotion
            for fc in function_calls:
                if fc.name == "show_emotion":
                    new_emotion = fc.arguments.get("emotion", current_emotion)
                    if emotion_manager.update_emotion(conv_id, new_emotion):
                        emotion_changed = True

            conv.add_assistant_message(content)

            # Send metadata first
            metadata = {
                "response": content,
                "emotion": {
                    "current": new_emotion,
                    "changed": emotion_changed,
                    "auto_reset": was_auto_reset
                },
                "function_calls": [{"name": fc.name, "arguments": fc.arguments} for fc in function_calls],
                "timing_ms": {"llm": timing_llm_ms}
            }
            yield f"event: metadata\ndata: {json.dumps(metadata)}\n\n"

            # TTS per sentence
            if config.tts.enabled and content.strip():
                tts = FishAudioTTS(
                    url=config.tts.url,
                    reference_id=config.tts.reference_id,
                    temperature=config.tts.temperature,
                    top_p=config.tts.top_p,
                    format=config.tts.format
                )

                sentences = split_into_sentences(content)
                for i, sentence in enumerate(sentences):
                    audio_b64, normalized = await tts.synthesize_base64(sentence)
                    audio_event = {
                        "sentence": sentence,
                        "normalized": normalized,
                        "audio_base64": audio_b64,
                        "index": i
                    }
                    yield f"event: audio\ndata: {json.dumps(audio_event)}\n\n"

                yield f"event: done\ndata: {json.dumps({'total_sentences': len(sentences)})}\n\n"
            else:
                yield f"event: done\ndata: {json.dumps({'total_sentences': 0})}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Wis conversation history."""
    conversation_manager = get_conversation_manager()
    emotion_manager = get_emotion_manager()

    deleted = conversation_manager.delete(conversation_id)
    emotion_manager.clear_state(conversation_id)

    if deleted:
        return {"status": "cleared", "conversation_id": conversation_id}
    return {"status": "not_found", "conversation_id": conversation_id}


@router.get("/conversations")
async def list_conversations():
    """Toon actieve conversations."""
    conversation_manager = get_conversation_manager()
    return conversation_manager.list_all()
