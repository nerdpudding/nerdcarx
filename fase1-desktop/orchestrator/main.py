#!/usr/bin/env python3
"""
NerdCarX Orchestrator - Met Function Calling + Vision
Verbindt STT (Voxtral) met LLM (Ministral via Ollama).

Configuratie: ../config.yml

Gebruik:
    uvicorn main:app --host 0.0.0.0 --port 8200 --reload
"""

import base64
import json
from pathlib import Path
from typing import Optional, List

import httpx
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# === CONFIG LADEN ===
CONFIG_PATH = Path(__file__).parent.parent / "config.yml"


def load_config() -> dict:
    """Laad configuratie uit config.yml."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config niet gevonden: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


# Laad config bij startup
config = load_config()

# Extract settings
OLLAMA_URL = config["ollama"]["url"]
OLLAMA_MODEL = config["ollama"]["model"]
OLLAMA_TEMPERATURE = config["ollama"]["temperature"]
OLLAMA_TOP_P = config["ollama"]["top_p"]
OLLAMA_REPEAT_PENALTY = config["ollama"]["repeat_penalty"]
OLLAMA_NUM_CTX = config["ollama"]["num_ctx"]
VOXTRAL_URL = config["voxtral"]["url"]
DEFAULT_SYSTEM_PROMPT = config["system_prompt"]
AVAILABLE_EMOTIONS = config["emotions"]
VISION_MOCK_IMAGE_PATH = Path(__file__).parent.parent / config["vision"]["mock_image_path"]


app = FastAPI(
    title="NerdCarX Orchestrator",
    description="Verbindt STT met LLM + Function Calling + Vision",
    version="0.3.0"
)


# === TOOLS DEFINITIE ===
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "show_emotion",
            "description": "Toon een emotie op het OLED display van de robot. Gebruik alleen bij duidelijke emotionele context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "emotion": {
                        "type": "string",
                        "enum": AVAILABLE_EMOTIONS,
                        "description": "De emotie om te tonen"
                    }
                },
                "required": ["emotion"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_photo",
            "description": "Maak een foto met de camera en analyseer wat je ziet. Gebruik bij vragen als 'wat zie je?', 'beschrijf je omgeving', 'kijk eens rond', of andere visuele vragen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "De vraag over wat je moet analyseren in de foto"
                    }
                },
                "required": ["question"]
            }
        }
    }
]


# === PYDANTIC MODELS ===
class FunctionCall(BaseModel):
    """Een function call van de LLM."""
    name: str
    arguments: dict


class ChatRequest(BaseModel):
    """Request voor chat endpoint."""
    message: str
    image_base64: Optional[str] = None  # Direct meegegeven image (legacy)
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    num_ctx: Optional[int] = None
    conversation_id: Optional[str] = None
    enable_tools: Optional[bool] = True


class ChatResponse(BaseModel):
    """Response van chat endpoint."""
    response: str
    model: str
    conversation_id: Optional[str] = None
    function_calls: Optional[List[FunctionCall]] = None


# In-memory conversation storage
conversations: dict = {}


# === TOOL EXECUTIE ===
async def load_mock_image() -> str:
    """Laad mock image als base64."""
    if not VISION_MOCK_IMAGE_PATH.exists():
        return ""
    with open(VISION_MOCK_IMAGE_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def execute_take_photo(args: dict, client: httpx.AsyncClient) -> str:
    """
    Maak een foto en analyseer deze.
    Voor nu: laad mock image van disk.
    Later: roep Pi camera endpoint aan.
    """
    question = args.get("question", "Beschrijf wat je ziet.")

    # Laad foto (mock)
    image_base64 = await load_mock_image()
    if not image_base64:
        return "Geen camera beschikbaar - kan geen foto maken."

    # Bouw vision prompt
    vision_prompt = f"Analyseer deze foto en beantwoord: {question}"

    # Aparte LLM call met de foto
    messages = [
        {"role": "system", "content": "Je bent de camera van een robot. Beschrijf feitelijk wat je ziet."},
        {"role": "user", "content": vision_prompt, "images": [image_base64]}
    ]

    options = {
        "temperature": OLLAMA_TEMPERATURE,
        "top_p": OLLAMA_TOP_P,
        "repeat_penalty": OLLAMA_REPEAT_PENALTY,
        "num_ctx": OLLAMA_NUM_CTX
    }

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
        "options": options
    }

    try:
        resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60.0)
        resp.raise_for_status()
        result = resp.json()
        return result["message"].get("content", "Kon de foto niet analyseren.")
    except Exception as e:
        return f"Fout bij foto analyse: {str(e)}"


async def execute_tool(name: str, args: dict, client: httpx.AsyncClient) -> str:
    """Voer een tool call uit."""
    if name == "show_emotion":
        emotion = args.get("emotion", "neutral")
        return f"Emotie '{emotion}' wordt getoond op het display."
    elif name == "take_photo":
        return await execute_take_photo(args, client)
    else:
        return f"Onbekende tool: {name}"


async def complete_tool_calls(
    client: httpx.AsyncClient,
    messages: list,
    tool_calls: list,
    options: dict
) -> tuple[str, list]:
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
            except:
                args = {}

        all_function_calls.append(FunctionCall(name=name, arguments=args))

        # Voer tool uit
        tool_result = await execute_tool(name, args, client)

        messages.append({
            "role": "tool",
            "content": tool_result
        })

    # Vraag om finale response (zonder tools)
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
        "options": options
    }

    resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
    resp.raise_for_status()
    result = resp.json()

    message = result["message"]
    content = message.get("content", "")

    # Check voor meer tool calls (recursief)
    new_tool_calls = message.get("tool_calls", [])
    if new_tool_calls:
        more_content, more_calls = await complete_tool_calls(
            client, messages, new_tool_calls, options
        )
        content = more_content
        all_function_calls.extend(more_calls)

    return content, all_function_calls


# === ENDPOINTS ===
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "orchestrator",
        "version": "0.3.0",
        "model": OLLAMA_MODEL
    }


@app.get("/status")
async def status():
    """Check status van alle services."""
    results = {
        "orchestrator": "ok",
        "config": str(CONFIG_PATH),
        "model": OLLAMA_MODEL
    }

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


@app.get("/config")
async def get_config():
    """Toon huidige configuratie (voor debugging)."""
    return {
        "ollama": {
            "url": OLLAMA_URL,
            "model": OLLAMA_MODEL,
            "temperature": OLLAMA_TEMPERATURE,
            "top_p": OLLAMA_TOP_P,
            "repeat_penalty": OLLAMA_REPEAT_PENALTY,
            "num_ctx": OLLAMA_NUM_CTX
        },
        "voxtral": {
            "url": VOXTRAL_URL
        },
        "vision": {
            "mock_image_path": str(VISION_MOCK_IMAGE_PATH),
            "mock_image_exists": VISION_MOCK_IMAGE_PATH.exists()
        },
        "emotions": AVAILABLE_EMOTIONS
    }


@app.get("/tools")
async def get_tools():
    """Toon beschikbare tools."""
    return {
        "tools": TOOLS,
        "emotions": AVAILABLE_EMOTIONS
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Stuur een bericht naar de LLM.
    Met optionele function calling.
    """
    system_prompt = request.system_prompt or DEFAULT_SYSTEM_PROMPT
    temperature = request.temperature or OLLAMA_TEMPERATURE
    num_ctx = request.num_ctx or OLLAMA_NUM_CTX

    # Bouw user message (met optionele image - legacy support)
    user_message = {"role": "user", "content": request.message}
    if request.image_base64:
        user_message["images"] = [request.image_base64]

    messages = [
        {"role": "system", "content": system_prompt},
        user_message
    ]

    options = {
        "temperature": temperature,
        "top_p": OLLAMA_TOP_P,
        "repeat_penalty": OLLAMA_REPEAT_PENALTY,
        "num_ctx": num_ctx
    }

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
        "options": options
    }

    if request.enable_tools:
        payload["tools"] = TOOLS

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            resp.raise_for_status()
            result = resp.json()

            message = result["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            function_calls = []

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
    temperature = request.temperature or OLLAMA_TEMPERATURE
    num_ctx = request.num_ctx or OLLAMA_NUM_CTX

    # Haal of maak conversation history
    if conv_id not in conversations:
        conversations[conv_id] = {
            "system_prompt": system_prompt,
            "messages": []
        }

    conv = conversations[conv_id]

    # Bouw user message (met optionele image - legacy)
    user_message = {"role": "user", "content": request.message}
    if request.image_base64:
        user_message["images"] = [request.image_base64]

    # Voeg user message toe aan history (zonder image - te groot)
    conv["messages"].append({"role": "user", "content": request.message})

    # Bouw messages array
    messages = [{"role": "system", "content": conv["system_prompt"]}]
    for i, msg in enumerate(conv["messages"]):
        if i == len(conv["messages"]) - 1 and msg["role"] == "user":
            messages.append(user_message)
        else:
            messages.append(msg.copy())

    options = {
        "temperature": temperature,
        "top_p": OLLAMA_TOP_P,
        "repeat_penalty": OLLAMA_REPEAT_PENALTY,
        "num_ctx": num_ctx
    }

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
        "options": options
    }

    if request.enable_tools is not False:
        payload["tools"] = TOOLS

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            resp.raise_for_status()
            result = resp.json()

            message = result["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            function_calls = []

            if tool_calls:
                content, function_calls = await complete_tool_calls(
                    client, messages, tool_calls, options
                )

            # Voeg response toe aan history
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
    """Toon actieve conversations."""
    return {
        conv_id: {
            "message_count": len(conv["messages"]),
            "system_prompt": conv["system_prompt"][:50] + "..."
        }
        for conv_id, conv in conversations.items()
    }


@app.post("/reload-config")
async def reload_config():
    """Herlaad config.yml (hot reload)."""
    global config, OLLAMA_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TOP_P
    global OLLAMA_REPEAT_PENALTY, OLLAMA_NUM_CTX, DEFAULT_SYSTEM_PROMPT
    global AVAILABLE_EMOTIONS, VISION_MOCK_IMAGE_PATH

    try:
        config = load_config()

        OLLAMA_MODEL = config["ollama"]["model"]
        OLLAMA_TEMPERATURE = config["ollama"]["temperature"]
        OLLAMA_TOP_P = config["ollama"]["top_p"]
        OLLAMA_REPEAT_PENALTY = config["ollama"]["repeat_penalty"]
        OLLAMA_NUM_CTX = config["ollama"]["num_ctx"]
        DEFAULT_SYSTEM_PROMPT = config["system_prompt"]
        AVAILABLE_EMOTIONS = config["emotions"]
        VISION_MOCK_IMAGE_PATH = Path(__file__).parent.parent / config["vision"]["mock_image_path"]

        return {"status": "ok", "message": "Config herladen", "model": OLLAMA_MODEL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config reload failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    host = config.get("orchestrator", {}).get("host", "0.0.0.0")
    port = config.get("orchestrator", {}).get("port", 8200)
    uvicorn.run(app, host=host, port=port)
