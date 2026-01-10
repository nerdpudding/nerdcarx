#!/usr/bin/env python3
"""
NerdCarX Orchestrator - Met Function Calling
Verbindt STT (Voxtral) met LLM (Ministral via Ollama).

Gebruik:
    uvicorn main:app --host 0.0.0.0 --port 8200 --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional, List, Any
import json

app = FastAPI(
    title="NerdCarX Orchestrator",
    description="Verbindt STT met LLM + Function Calling",
    version="0.2.0"
)

# Configuratie - later evt naar config file
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "ministral-3:8b-instruct-2512-q8_0"
VOXTRAL_URL = "http://localhost:8150"

# Default settings
DEFAULT_NUM_CTX = 65536  # 64k context
DEFAULT_TEMPERATURE = 0.7

# Beschikbare emoties voor de robot
AVAILABLE_EMOTIONS = ["happy", "sad", "angry", "surprised", "neutral", "curious", "confused", "excited", "thinking"]

# Tools definitie voor Ollama/Ministral
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "show_emotion",
            "description": "Toon een emotie op het robotgezicht als reactie op wat de gebruiker zegt. Gebruik dit om de robot expressief te maken.",
            "parameters": {
                "type": "object",
                "properties": {
                    "emotion": {
                        "type": "string",
                        "enum": AVAILABLE_EMOTIONS,
                        "description": "De emotie om te tonen: happy, sad, angry, surprised, neutral, curious, confused, excited, thinking"
                    }
                },
                "required": ["emotion"]
            }
        }
    }
]

# System prompt met function calling instructies
DEFAULT_SYSTEM_PROMPT = """Je bent NerdCarX, een vriendelijke en behulpzame robot assistent.
Je geeft korte, duidelijke antwoorden in het Nederlands.
Je bent nieuwsgierig en hebt een licht humoristische persoonlijkheid.

EMOTIE INSTRUCTIES - VERPLICHT:
Je hebt een OLED display waarop je emoties toont via de show_emotion TOOL.

BELANGRIJK: Gebruik ALTIJD de show_emotion tool - NOOIT als tekst schrijven!
FOUT: *show_emotion("happy")* of (show_emotion: happy) in je tekst
GOED: Roep de show_emotion functie aan via de tool interface

Emoties:
- happy: positief, complimenten, grappen
- sad: verdriet
- angry: frustratie, boosheid
- surprised: onverwacht
- curious: interessante vragen
- confused: onduidelijk
- excited: enthousiasme
- thinking: complex uitleggen
- neutral: informatief

Roep show_emotion aan bij ELKE response via de tool, niet als tekst!"""


class FunctionCall(BaseModel):
    """Een function call van de LLM."""
    name: str
    arguments: dict


class ChatRequest(BaseModel):
    """Request voor chat endpoint."""
    message: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    num_ctx: Optional[int] = None
    conversation_id: Optional[str] = None
    enable_tools: Optional[bool] = True  # Function calling aan/uit


class ChatResponse(BaseModel):
    """Response van chat endpoint."""
    response: str
    model: str
    conversation_id: Optional[str] = None
    function_calls: Optional[List[FunctionCall]] = None


class TranscribeAndChatRequest(BaseModel):
    """Request voor transcribe + chat in één call."""
    audio_base64: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None


# In-memory conversation storage (simpel voor nu)
conversations: dict = {}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "orchestrator", "version": "0.2.0"}


@app.get("/status")
async def status():
    """Check status van alle services."""
    results = {"orchestrator": "ok"}

    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            results["ollama"] = "ok" if resp.status_code == 200 else "error"
    except Exception:
        results["ollama"] = "unreachable"

    # Check Voxtral
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{VOXTRAL_URL}/health")
            results["voxtral"] = "ok" if resp.status_code == 200 else "error"
    except Exception:
        results["voxtral"] = "unreachable"

    return results


@app.get("/tools")
async def get_tools():
    """Toon beschikbare tools."""
    return {
        "tools": TOOLS,
        "emotions": AVAILABLE_EMOTIONS
    }


async def complete_tool_calls(client: httpx.AsyncClient, messages: list, tool_calls: list, options: dict) -> tuple[str, list]:
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

    # "Voer" elke tool call uit en stuur resultaat terug
    for tc in tool_calls:
        func = tc.get("function", {})
        name = func.get("name", "")
        args = func.get("arguments", {})

        # Bewaar voor response
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except:
                args = {}
        all_function_calls.append(FunctionCall(name=name, arguments=args))

        # Simuleer tool resultaat (emotie wordt later door client getoond)
        tool_result = "ok"
        if name == "show_emotion":
            emotion = args.get("emotion", "neutral")
            tool_result = f"Emotie '{emotion}' wordt getoond op het display."

        messages.append({
            "role": "tool",
            "content": tool_result
        })

    # Vraag om finale response (zonder tools, we willen nu tekst)
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
        "options": options
        # Geen tools hier - we willen dat het model nu tekst geeft
    }

    resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
    resp.raise_for_status()
    result = resp.json()

    message = result["message"]
    content = message.get("content", "")

    # Check voor meer tool calls (recursief)
    new_tool_calls = message.get("tool_calls", [])
    if new_tool_calls:
        more_content, more_calls = await complete_tool_calls(client, messages, new_tool_calls, options)
        content = more_content
        all_function_calls.extend(more_calls)

    return content, all_function_calls


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Stuur een bericht naar de LLM en krijg een response.
    Met optionele function calling.
    """
    system_prompt = request.system_prompt or DEFAULT_SYSTEM_PROMPT
    temperature = request.temperature or DEFAULT_TEMPERATURE
    num_ctx = request.num_ctx or DEFAULT_NUM_CTX

    # Bouw messages array
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message}
    ]

    options = {
        "temperature": temperature,
        "num_ctx": num_ctx
    }

    # Ollama API call
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
        "options": options
    }

    # Voeg tools toe als enabled
    if request.enable_tools:
        payload["tools"] = TOOLS

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()

            message = result["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            function_calls = []

            # Als er tool calls zijn, voer ze uit en krijg finale response
            if tool_calls:
                content, function_calls = await complete_tool_calls(
                    client, messages, tool_calls, options
                )

            return ChatResponse(
                response=content,
                model=OLLAMA_MODEL,
                conversation_id=request.conversation_id,
                function_calls=function_calls if function_calls else None
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama niet bereikbaar")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversation", response_model=ChatResponse)
async def conversation(request: ChatRequest):
    """
    Chat met conversation history en function calling.
    """
    conv_id = request.conversation_id or "default"
    system_prompt = request.system_prompt or DEFAULT_SYSTEM_PROMPT
    temperature = request.temperature or DEFAULT_TEMPERATURE
    num_ctx = request.num_ctx or DEFAULT_NUM_CTX

    # Haal of maak conversation history
    if conv_id not in conversations:
        conversations[conv_id] = {
            "system_prompt": system_prompt,
            "messages": []
        }

    conv = conversations[conv_id]

    # Voeg user message toe
    conv["messages"].append({"role": "user", "content": request.message})

    # Bouw volledige messages array (kopie voor API call)
    messages = [{"role": "system", "content": conv["system_prompt"]}]
    messages.extend([msg.copy() for msg in conv["messages"]])

    options = {
        "temperature": temperature,
        "num_ctx": num_ctx
    }

    # Ollama API call
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
        "options": options
    }

    # Voeg tools toe als enabled
    if request.enable_tools is not False:
        payload["tools"] = TOOLS

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()

            message = result["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            function_calls = []

            # Als er tool calls zijn, voer ze uit en krijg finale response
            if tool_calls:
                content, function_calls = await complete_tool_calls(
                    client, messages, tool_calls, options
                )

            # Voeg alleen finale tekst response toe aan history
            conv["messages"].append({"role": "assistant", "content": content})

            return ChatResponse(
                response=content,
                model=OLLAMA_MODEL,
                conversation_id=conv_id,
                function_calls=function_calls if function_calls else None
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama niet bereikbaar")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Wis conversation history."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"status": "cleared", "conversation_id": conversation_id}
    return {"status": "not_found", "conversation_id": conversation_id}


@app.get("/conversations")
async def list_conversations():
    """Toon actieve conversations (voor debugging)."""
    return {
        conv_id: {
            "message_count": len(conv["messages"]),
            "system_prompt": conv["system_prompt"][:50] + "..."
        }
        for conv_id, conv in conversations.items()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
