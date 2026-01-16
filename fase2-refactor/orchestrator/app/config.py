"""
Configuration loading met environment variable support.
Ondersteunt ${VAR:-default} syntax voor Docker integratie.
"""
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class OllamaConfig:
    url: str = "http://localhost:11434"
    model: str = "ministral-3:14b"
    temperature: float = 0.15
    top_p: float = 1.0
    repeat_penalty: float = 1.0
    num_ctx: int = 65536


@dataclass
class VoxtralConfig:
    url: str = "http://localhost:8150"
    model: str = "mistralai/Voxtral-Mini-3B-2507"
    temperature: float = 0.0


@dataclass
class OrchestratorConfig:
    host: str = "0.0.0.0"
    port: int = 8200


@dataclass
class VisionConfig:
    mock_image_path: str = "test_images/test_foto.jpg"
    pi_camera_url: Optional[str] = None


@dataclass
class EmotionsConfig:
    default: str = "neutral"
    auto_reset_minutes: int = 5
    available: list[str] = field(default_factory=lambda: [
        "happy", "sad", "angry", "surprised", "neutral",
        "curious", "confused", "excited", "thinking", "shy",
        "love", "tired", "bored", "proud", "worried"
    ])


@dataclass
class TTSConfig:
    url: str = "http://localhost:8250"
    enabled: bool = True
    reference_id: str = "dutch2"
    temperature: float = 0.5
    top_p: float = 0.6
    format: str = "wav"
    streaming: bool = True


@dataclass
class WebSocketConfig:
    enabled: bool = True
    heartbeat_interval: int = 30
    audio_chunk_threshold: int = 3


@dataclass
class AppConfig:
    """Centrale applicatie configuratie."""
    ollama: OllamaConfig
    voxtral: VoxtralConfig
    orchestrator: OrchestratorConfig
    vision: VisionConfig
    emotions: EmotionsConfig
    tts: TTSConfig
    websocket: WebSocketConfig
    system_prompt: str = ""


def expand_env_vars(value: str) -> str:
    """
    Expand ${VAR:-default} patterns in string values.

    Examples:
        ${OLLAMA_URL:-http://localhost:11434} -> value of OLLAMA_URL or default
    """
    pattern = r'\$\{([^}:]+)(?::-([^}]*))?\}'

    def replace(match):
        var_name = match.group(1)
        default = match.group(2) or ""
        return os.environ.get(var_name, default)

    return re.sub(pattern, replace, value)


def process_config_values(data: dict) -> dict:
    """Recursively process config values, expanding env vars in strings."""
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = expand_env_vars(value)
        elif isinstance(value, dict):
            result[key] = process_config_values(value)
        elif isinstance(value, list):
            result[key] = [
                expand_env_vars(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Laad configuratie uit YAML bestand met env var expansie.

    Args:
        config_path: Pad naar config.yml. Default: /app/config.yml (Docker)
                     of ../config.yml (development)
    """
    if config_path is None:
        # Docker mount path
        docker_path = Path("/app/config.yml")
        # Development path (relatief aan app/)
        dev_path = Path(__file__).parent.parent.parent / "config.yml"

        config_path = docker_path if docker_path.exists() else dev_path

    if not config_path.exists():
        raise FileNotFoundError(f"Config niet gevonden: {config_path}")

    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    # Process env vars
    config = process_config_values(raw_config)

    # Build typed config objects
    return AppConfig(
        ollama=OllamaConfig(**config.get("ollama", {})),
        voxtral=VoxtralConfig(**config.get("voxtral", {})),
        orchestrator=OrchestratorConfig(**config.get("orchestrator", {})),
        vision=VisionConfig(**config.get("vision", {})),
        emotions=EmotionsConfig(**config.get("emotions", {})),
        tts=TTSConfig(**config.get("tts", {})),
        websocket=WebSocketConfig(**config.get("websocket", {})),
        system_prompt=config.get("system_prompt", "")
    )


# Global config instance (lazy loaded)
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or load the global config instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> AppConfig:
    """Force reload of config (hot reload support)."""
    global _config
    _config = load_config()
    return _config
