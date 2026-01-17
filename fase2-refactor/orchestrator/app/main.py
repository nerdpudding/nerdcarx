#!/usr/bin/env python3
"""
NerdCarX Orchestrator - Fase 2
FastAPI entry point (slim).

Gebruik:
    uvicorn app.main:app --host 0.0.0.0 --port 8200 --reload
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import get_config
from .routes import health_router, chat_router, websocket_router
from .services import OllamaLLM


async def warmup_ollama(config) -> None:
    """
    Warmup Ollama door model te laden in VRAM.

    Stuurt een simpele request zodat het model geladen wordt.
    Door OLLAMA_KEEP_ALIVE=-1 blijft het model in VRAM.
    """
    print("Warming up Ollama (loading model into VRAM)...")
    try:
        llm = OllamaLLM(
            url=config.ollama.url,
            model=config.ollama.model,
            timeout=180.0  # Extra tijd voor eerste load
        )
        # Simpele warmup request
        await llm.chat(messages=[{"role": "user", "content": "hoi"}])
        print("Ollama warmup complete - model loaded in VRAM")
    except Exception as e:
        print(f"Ollama warmup failed: {e}")
        print("First request will be slow (cold start)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    config = get_config()
    print(f"NerdCarX Orchestrator v0.4.0 starting...")
    print(f"LLM: {config.ollama.model} @ {config.ollama.url}")
    print(f"STT: Voxtral @ {config.voxtral.url}")
    print(f"TTS: Fish Audio @ {config.tts.url} (enabled={config.tts.enabled})")
    print(f"WebSocket: enabled={config.websocket.enabled}")

    # Warmup Ollama in background (niet blocking)
    asyncio.create_task(warmup_ollama(config))

    yield

    # Shutdown
    print("Orchestrator shutting down...")


app = FastAPI(
    title="NerdCarX Orchestrator",
    description="Verbindt STT met LLM + Function Calling + Vision + WebSocket",
    version="0.4.0",
    lifespan=lifespan
)

# Register routes
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(websocket_router)


if __name__ == "__main__":
    import uvicorn
    config = get_config()
    uvicorn.run(
        app,
        host=config.orchestrator.host,
        port=config.orchestrator.port
    )
