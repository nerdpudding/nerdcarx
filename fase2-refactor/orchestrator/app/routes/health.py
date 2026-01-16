"""Health check en status endpoints."""
from fastapi import APIRouter

from ..config import get_config, reload_config
from ..services import OllamaLLM, VoxtralSTT, FishAudioTTS

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Health check endpoint."""
    config = get_config()
    return {
        "status": "ok",
        "service": "orchestrator",
        "version": "0.4.0",
        "model": config.ollama.model
    }


@router.get("/status")
async def status():
    """Check status van alle services."""
    config = get_config()

    results = {
        "orchestrator": "ok",
        "model": config.ollama.model
    }

    # Check Ollama
    llm = OllamaLLM(url=config.ollama.url)
    results["ollama"] = "ok" if await llm.health_check() else "unreachable"

    # Check Voxtral
    stt = VoxtralSTT(url=config.voxtral.url)
    results["voxtral"] = "ok" if await stt.health_check() else "unreachable"

    # Check TTS
    if config.tts.enabled:
        tts = FishAudioTTS(url=config.tts.url)
        results["tts"] = "ok" if await tts.health_check() else "unreachable"
    else:
        results["tts"] = "disabled"

    return results


@router.get("/config")
async def get_current_config():
    """Toon huidige configuratie (voor debugging)."""
    config = get_config()
    return {
        "ollama": {
            "url": config.ollama.url,
            "model": config.ollama.model,
            "temperature": config.ollama.temperature,
            "top_p": config.ollama.top_p,
            "repeat_penalty": config.ollama.repeat_penalty,
            "num_ctx": config.ollama.num_ctx
        },
        "voxtral": {
            "url": config.voxtral.url,
            "model": config.voxtral.model
        },
        "vision": {
            "mock_image_path": config.vision.mock_image_path,
            "pi_camera_url": config.vision.pi_camera_url
        },
        "emotions": {
            "available": config.emotions.available,
            "default": config.emotions.default,
            "auto_reset_minutes": config.emotions.auto_reset_minutes
        },
        "tts": {
            "url": config.tts.url,
            "enabled": config.tts.enabled,
            "reference_id": config.tts.reference_id,
            "temperature": config.tts.temperature,
            "top_p": config.tts.top_p,
            "format": config.tts.format,
            "streaming": config.tts.streaming
        },
        "websocket": {
            "enabled": config.websocket.enabled,
            "heartbeat_interval": config.websocket.heartbeat_interval
        }
    }


@router.get("/tools")
async def get_tools():
    """Toon beschikbare tools."""
    config = get_config()
    from ..services.tools import EmotionTool
    emotion_tool = EmotionTool(available_emotions=config.emotions.available)
    from ..services.tools import VisionTool
    vision_tool = VisionTool()

    return {
        "tools": [emotion_tool.definition, vision_tool.definition],
        "emotions": config.emotions.available
    }


@router.post("/reload-config")
async def do_reload_config():
    """Herlaad config.yml (hot reload)."""
    try:
        config = reload_config()
        return {
            "status": "ok",
            "message": "Config herladen",
            "model": config.ollama.model,
            "tts_enabled": config.tts.enabled,
            "tts_streaming": config.tts.streaming
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
