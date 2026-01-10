#!/usr/bin/env python3
"""
NerdCarX Orchestrator - Simpele versie
Verbindt STT (Voxtral) met LLM (Ministral via Ollama).

Gebruik:
    uvicorn main:app --host 0.0.0.0 --port 8200 --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional
import json

app = FastAPI(
    title="NerdCarX Orchestrator",
    description="Verbindt STT met LLM",
    version="0.1.0"
)

# Configuratie - later evt naar config file
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "ministral-3:8b-instruct-2512-q8_0"
VOXTRAL_URL = "http://localhost:8150"

# Default settings
DEFAULT_NUM_CTX = 65536  # 64k context
DEFAULT_TEMPERATURE = 0.7
DEFAULT_SYSTEM_PROMPT = """Je bent NerdCarX, een vriendelijke en behulpzame robot assistent.
Je geeft korte, duidelijke antwoorden in het Nederlands.
Je bent nieuwsgierig en hebt een licht humoristische persoonlijkheid."""


class ChatRequest(BaseModel):
    """Request voor chat endpoint."""
    message: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    num_ctx: Optional[int] = None
    conversation_id: Optional[str] = None  # Voor later: conversation tracking


class ChatResponse(BaseModel):
    """Response van chat endpoint."""
    response: str
    model: str
    conversation_id: Optional[str] = None


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
    return {"status": "ok", "service": "orchestrator"}


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


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Stuur een bericht naar de LLM en krijg een response.

    Dit is de kern van de orchestrator - ontvangt tekst (van STT of direct)
    en stuurt door naar Ollama.
    """
    system_prompt = request.system_prompt or DEFAULT_SYSTEM_PROMPT
    temperature = request.temperature or DEFAULT_TEMPERATURE
    num_ctx = request.num_ctx or DEFAULT_NUM_CTX

    # Bouw messages array
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message}
    ]

    # Ollama API call
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()

            return ChatResponse(
                response=result["message"]["content"],
                model=OLLAMA_MODEL,
                conversation_id=request.conversation_id
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
    Chat met conversation history.

    Gebruik conversation_id om context te behouden over meerdere berichten.
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

    # Bouw volledige messages array
    messages = [{"role": "system", "content": conv["system_prompt"]}]
    messages.extend(conv["messages"])

    # Ollama API call
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()

            assistant_response = result["message"]["content"]

            # Voeg assistant response toe aan history
            conv["messages"].append({"role": "assistant", "content": assistant_response})

            return ChatResponse(
                response=assistant_response,
                model=OLLAMA_MODEL,
                conversation_id=conv_id
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
