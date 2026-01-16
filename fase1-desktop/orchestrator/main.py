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
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

import asyncio
import httpx
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from num2words import num2words
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
AVAILABLE_EMOTIONS = config["emotions"]["available"]
DEFAULT_EMOTION = config["emotions"]["default"]
AUTO_RESET_MINUTES = config["emotions"]["auto_reset_minutes"]
VISION_MOCK_IMAGE_PATH = Path(__file__).parent.parent / config["vision"]["mock_image_path"]

# TTS settings (Fish Audio S1-mini)
TTS_CONFIG = config.get("tts", {})
TTS_URL = TTS_CONFIG.get("url", "http://localhost:8250")
TTS_ENABLED = TTS_CONFIG.get("enabled", True)
TTS_REFERENCE_ID = TTS_CONFIG.get("reference_id", "dutch2")
TTS_TEMPERATURE = TTS_CONFIG.get("temperature", 0.2)
TTS_TOP_P = TTS_CONFIG.get("top_p", 0.5)
TTS_FORMAT = TTS_CONFIG.get("format", "wav")
TTS_STREAMING = TTS_CONFIG.get("streaming", False)


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
    emotion: Optional[dict] = None  # {"current": "angry", "changed": true, "auto_reset": false}
    audio_base64: Optional[str] = None  # TTS audio als base64
    timing_ms: Optional[dict] = None  # {"llm": 1234, "tts": 567}
    normalized_text: Optional[str] = None  # TTS genormaliseerde tekst (voor debug)


# In-memory conversation storage
conversations: dict = {}

# In-memory emotion state storage
emotion_states: dict = {}


# === EMOTION STATE MANAGEMENT ===
class EmotionInfo(BaseModel):
    """Emotie state info in response."""
    current: str
    changed: bool
    auto_reset: bool = False


def get_emotion_state(conversation_id: str) -> dict:
    """Haal huidige emotie state op, met auto-reset check."""
    if conversation_id not in emotion_states:
        emotion_states[conversation_id] = {
            "emotion": DEFAULT_EMOTION,
            "last_updated": datetime.now(),
            "last_interaction": datetime.now()
        }
        return emotion_states[conversation_id]

    state = emotion_states[conversation_id]

    # Check auto-reset
    if datetime.now() - state["last_interaction"] > timedelta(minutes=AUTO_RESET_MINUTES):
        if state["emotion"] != DEFAULT_EMOTION:
            state["emotion"] = DEFAULT_EMOTION
            state["last_updated"] = datetime.now()
            state["auto_reset"] = True
        else:
            state["auto_reset"] = False
    else:
        state["auto_reset"] = False

    state["last_interaction"] = datetime.now()
    return state


def update_emotion_state(conversation_id: str, emotion: str) -> None:
    """Update emotie state."""
    if conversation_id not in emotion_states:
        emotion_states[conversation_id] = {
            "emotion": emotion,
            "last_updated": datetime.now(),
            "last_interaction": datetime.now()
        }
    else:
        emotion_states[conversation_id]["emotion"] = emotion
        emotion_states[conversation_id]["last_updated"] = datetime.now()
        emotion_states[conversation_id]["last_interaction"] = datetime.now()


# === TTS TEXT NORMALISATIE ===
# Nederlandse fonetische uitspraak voor letters
NL_LETTER_SOUNDS = {
    'A': 'aa', 'B': 'bee', 'C': 'see', 'D': 'dee', 'E': 'ee',
    'F': 'ef', 'G': 'zjee', 'H': 'haa', 'I': 'ie', 'J': 'jee',
    'K': 'kaa', 'L': 'el', 'M': 'em', 'N': 'en', 'O': 'oo',
    'P': 'pee', 'Q': 'kuu', 'R': 'er', 'S': 'es', 'T': 'tee',
    'U': 'uu', 'V': 'vee', 'W': 'wee', 'X': 'iks', 'Y': 'ei',
    'Z': 'zet'
}

# Woorden die NIET fonetisch gespeld moeten worden (klinken al goed)
SKIP_ACRONYMS = {'OK', 'TV', 'AI', 'WC'}

# Specifieke woord vervangingen (Engels → Nederlands-klinkend)
WORD_REPLACEMENTS = {
    r'\bDocker\b': 'dokker',
    r'\bPython\b': 'paiton',
    r'\bdesktop\b': 'desktob',
}


def normalize_for_tts(text: str) -> str:
    """
    Normaliseer tekst voor betere Nederlandse TTS uitspraak.

    - Acroniemen (API, USB) → Nederlandse fonetiek (aa-pee-ie, joe-es-bee)
    - Getallen → Nederlandse woorden (150 → honderdvijftig)
    - Haakjes → eerste ( wordt komma, rest verwijderd
    - Specifieke Engelse woorden → Nederlands-klinkend
    """

    # 1. HAAKJES: eerste ( wordt ", ", daarna haakjes verwijderen
    # "extreme ultraviolet (EUV)" → "extreme ultraviolet, EUV"
    text = re.sub(r'\s*\(', ', ', text, count=1)  # Eerste ( → ", "
    text = re.sub(r'[()]', '', text)  # Overige haakjes verwijderen

    # 2. ACRONIEMEN: letter-voor-letter uitspreken
    def spell_acronym(match):
        acronym = match.group(0)
        if acronym in SKIP_ACRONYMS:
            return acronym
        return '-'.join(NL_LETTER_SOUNDS.get(c, c) for c in acronym)

    # Match 2+ hoofdletters als heel woord
    text = re.sub(r'\b[A-Z]{2,}\b', spell_acronym, text)

    # 3. SPECIFIEKE WOORDEN
    for pattern, replacement in WORD_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 4. GETALLEN: naar Nederlandse woorden
    def replace_number(match):
        num_str = match.group(0)
        try:
            # Decimalen: "2.5" → "twee komma vijf"
            if '.' in num_str:
                parts = num_str.split('.')
                whole = num2words(int(parts[0]), lang='nl')
                decimal = ' '.join(num2words(int(d), lang='nl') for d in parts[1])
                return f"{whole} komma {decimal}"
            # Gewone getallen
            return num2words(int(num_str), lang='nl')
        except:
            return num_str

    # Match getallen (geen ranges voor nu)
    text = re.sub(r'\b\d+(?:\.\d+)?\b', replace_number, text)

    return text


def split_into_sentences(text: str) -> list[str]:
    """
    Split tekst in zinnen voor pseudo-streaming TTS.
    Behoudt interpunctie en filtert lege zinnen.
    """
    # Split op . ! ? gevolgd door spatie of einde string
    # Maar niet op afkortingen als "bv." of "nr."
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Filter lege zinnen en strip whitespace
    return [s.strip() for s in sentences if s.strip()]


# === TTS SERVICE (Fish Audio S1-mini) ===
async def synthesize_speech(text: str, emotion: str, client: httpx.AsyncClient) -> tuple[Optional[str], Optional[str]]:
    """
    Roep Fish Audio TTS service aan om tekst naar spraak te converteren.
    Returns: (base64 encoded audio, normalized_text) of (None, None) bij fout.

    Note: emotion parameter wordt behouden voor interface compatibiliteit,
    maar Fish Audio gebruikt reference_id voor stem consistentie.
    """
    if not TTS_ENABLED or not text.strip():
        return None, None

    # Normaliseer tekst voor betere Nederlandse uitspraak
    normalized_text = normalize_for_tts(text)

    try:
        payload = {
            "text": normalized_text,
            "reference_id": TTS_REFERENCE_ID,
            "temperature": TTS_TEMPERATURE,
            "top_p": TTS_TOP_P,
            "format": TTS_FORMAT
        }

        resp = await client.post(
            f"{TTS_URL}/v1/tts",
            json=payload,
            timeout=30.0
        )
        resp.raise_for_status()

        # Audio bytes naar base64
        audio_bytes = resp.content
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        # Return alleen normalized_text als het verschilt van origineel
        if normalized_text != text:
            return audio_base64, normalized_text
        return audio_base64, None
    except Exception as e:
        print(f"TTS error: {e}")
        return None, None


# === TEXT-BASED TOOL CALL PARSING ===
def parse_text_tool_calls(content: str) -> tuple[str, list]:
    """
    Parse tool calls uit tekst content.
    Mistral format: functionname[ARGS]{json}

    Returns: (cleaned_content, list of FunctionCall)
    """
    # Pattern voor Mistral text-based tool calls: functionname[ARGS]{json}
    pattern = r'(\w+)\[ARGS\](\{[^}]+\})'
    matches = re.findall(pattern, content)

    function_calls = []
    for name, args_str in matches:
        try:
            args = json.loads(args_str)
            function_calls.append(FunctionCall(name=name, arguments=args))
        except json.JSONDecodeError:
            continue

    # Verwijder tool call tekst uit content
    cleaned = re.sub(pattern, '', content).strip()

    return cleaned, function_calls


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

    # Check TTS (Fish Audio)
    if TTS_ENABLED:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{TTS_URL}/v1/health")
                results["tts"] = "ok" if resp.status_code == 200 else "error"
        except Exception:
            results["tts"] = "unreachable"
    else:
        results["tts"] = "disabled"

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
        "emotions": {
            "available": AVAILABLE_EMOTIONS,
            "default": DEFAULT_EMOTION,
            "auto_reset_minutes": AUTO_RESET_MINUTES
        },
        "tts": {
            "url": TTS_URL,
            "enabled": TTS_ENABLED,
            "reference_id": TTS_REFERENCE_ID,
            "temperature": TTS_TEMPERATURE,
            "top_p": TTS_TOP_P,
            "format": TTS_FORMAT,
            "streaming": TTS_STREAMING
        }
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
    Chat met conversation history, function calling, en emotion state.
    """
    conv_id = request.conversation_id or "default"
    system_prompt = request.system_prompt or DEFAULT_SYSTEM_PROMPT
    temperature = request.temperature or OLLAMA_TEMPERATURE
    num_ctx = request.num_ctx or OLLAMA_NUM_CTX

    # Haal emotion state op (inclusief auto-reset check)
    emotion_state = get_emotion_state(conv_id)
    current_emotion = emotion_state["emotion"]
    was_auto_reset = emotion_state.get("auto_reset", False)

    # Voeg huidige emotie toe aan system prompt
    emotion_context = f"\n\nJe huidige emotionele staat is: {current_emotion}. Verander deze alleen als de interactie daar aanleiding toe geeft."
    enhanced_system_prompt = system_prompt + emotion_context

    # Haal of maak conversation history
    if conv_id not in conversations:
        conversations[conv_id] = {
            "system_prompt": system_prompt,  # Originele prompt opslaan
            "messages": []
        }

    conv = conversations[conv_id]

    # Bouw user message (met optionele image - legacy)
    user_message = {"role": "user", "content": request.message}
    if request.image_base64:
        user_message["images"] = [request.image_base64]

    # Voeg user message toe aan history (zonder image - te groot)
    conv["messages"].append({"role": "user", "content": request.message})

    # Bouw messages array (met enhanced system prompt)
    messages = [{"role": "system", "content": enhanced_system_prompt}]
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
            # === TIMING: LLM START ===
            t_llm_start = time.perf_counter()

            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            resp.raise_for_status()
            result = resp.json()

            message = result["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            function_calls = []

            # Check eerst Ollama native tool calls
            if tool_calls:
                content, function_calls = await complete_tool_calls(
                    client, messages, tool_calls, options
                )
            else:
                # Fallback: parse tool calls uit tekst (Mistral format)
                content, function_calls = parse_text_tool_calls(content)

                # Voer geparseerde tool calls uit
                for fc in function_calls:
                    await execute_tool(fc.name, fc.arguments, client)

            # === TIMING: LLM END ===
            t_llm_end = time.perf_counter()
            timing_llm_ms = (t_llm_end - t_llm_start) * 1000

            # Check of emotie is veranderd via function call
            emotion_changed = False
            new_emotion = current_emotion
            for fc in function_calls:
                if fc.name == "show_emotion":
                    new_emotion = fc.arguments.get("emotion", current_emotion)
                    if new_emotion != current_emotion:
                        update_emotion_state(conv_id, new_emotion)
                        emotion_changed = True

            # Voeg response toe aan history
            conv["messages"].append({"role": "assistant", "content": content})

            # Check of er een show_emotion tool call was
            had_emotion_tool_call = any(fc.name == "show_emotion" for fc in function_calls)

            # === TIMING: TTS START ===
            t_tts_start = time.perf_counter()

            # TTS: genereer spraak van schone tekst (geen function calls!)
            audio_base64, normalized_text = await synthesize_speech(content, new_emotion, client)

            # === TIMING: TTS END ===
            t_tts_end = time.perf_counter()
            timing_tts_ms = (t_tts_end - t_tts_start) * 1000

            return ChatResponse(
                response=content,
                model=OLLAMA_MODEL,
                conversation_id=conv_id,
                function_calls=function_calls if function_calls else None,
                emotion={
                    "current": new_emotion,
                    "changed": emotion_changed,
                    "auto_reset": was_auto_reset,
                    "had_tool_call": had_emotion_tool_call
                },
                audio_base64=audio_base64,
                timing_ms={
                    "llm": round(timing_llm_ms),
                    "tts": round(timing_tts_ms)
                },
                normalized_text=normalized_text
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama niet bereikbaar")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversation/streaming")
async def conversation_streaming(request: ChatRequest):
    """
    Streaming conversation endpoint.
    Stuurt LLM response als tekst, gevolgd door TTS audio per zin als SSE events.

    Response format (Server-Sent Events):
        event: metadata
        data: {"response": "...", "emotion": {...}, "function_calls": [...]}

        event: audio
        data: {"sentence": "Eerste zin.", "audio_base64": "...", "index": 0}

        event: audio
        data: {"sentence": "Tweede zin.", "audio_base64": "...", "index": 1}

        event: done
        data: {"total_sentences": 2}
    """
    conv_id = request.conversation_id or "default"
    system_prompt = request.system_prompt or DEFAULT_SYSTEM_PROMPT
    temperature = request.temperature or OLLAMA_TEMPERATURE
    num_ctx = request.num_ctx or OLLAMA_NUM_CTX

    # Haal emotion state op
    emotion_state = get_emotion_state(conv_id)
    current_emotion = emotion_state["emotion"]
    was_auto_reset = emotion_state.get("auto_reset", False)

    emotion_context = f"\n\nJe huidige emotionele staat is: {current_emotion}. Verander deze alleen als de interactie daar aanleiding toe geeft."
    enhanced_system_prompt = system_prompt + emotion_context

    # Haal of maak conversation history
    if conv_id not in conversations:
        conversations[conv_id] = {
            "system_prompt": system_prompt,
            "messages": []
        }
    conv = conversations[conv_id]

    user_message = {"role": "user", "content": request.message}
    conv["messages"].append({"role": "user", "content": request.message})

    messages = [{"role": "system", "content": enhanced_system_prompt}]
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

    async def generate_stream():
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # LLM call
                t_llm_start = time.perf_counter()
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
                else:
                    content, function_calls = parse_text_tool_calls(content)
                    for fc in function_calls:
                        await execute_tool(fc.name, fc.arguments, client)

                t_llm_end = time.perf_counter()
                timing_llm_ms = round((t_llm_end - t_llm_start) * 1000)

                # Check emotie verandering
                emotion_changed = False
                new_emotion = current_emotion
                for fc in function_calls:
                    if fc.name == "show_emotion":
                        new_emotion = fc.arguments.get("emotion", current_emotion)
                        if new_emotion != current_emotion:
                            update_emotion_state(conv_id, new_emotion)
                            emotion_changed = True

                conv["messages"].append({"role": "assistant", "content": content})

                # Stuur metadata eerst
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

                # Split in zinnen en genereer TTS per zin
                sentences = split_into_sentences(content)

                for i, sentence in enumerate(sentences):
                    audio_base64, normalized_text = await synthesize_speech(sentence, new_emotion, client)

                    audio_event = {
                        "sentence": sentence,
                        "normalized": normalized_text,
                        "audio_base64": audio_base64,
                        "index": i
                    }
                    yield f"event: audio\ndata: {json.dumps(audio_event)}\n\n"

                # Done event
                yield f"event: done\ndata: {json.dumps({'total_sentences': len(sentences)})}\n\n"

        except Exception as e:
            error_event = {"error": str(e)}
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


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
    global AVAILABLE_EMOTIONS, DEFAULT_EMOTION, AUTO_RESET_MINUTES, VISION_MOCK_IMAGE_PATH
    global TTS_CONFIG, TTS_URL, TTS_ENABLED, TTS_REFERENCE_ID, TTS_TEMPERATURE, TTS_TOP_P, TTS_FORMAT, TTS_STREAMING

    try:
        config = load_config()

        OLLAMA_MODEL = config["ollama"]["model"]
        OLLAMA_TEMPERATURE = config["ollama"]["temperature"]
        OLLAMA_TOP_P = config["ollama"]["top_p"]
        OLLAMA_REPEAT_PENALTY = config["ollama"]["repeat_penalty"]
        OLLAMA_NUM_CTX = config["ollama"]["num_ctx"]
        DEFAULT_SYSTEM_PROMPT = config["system_prompt"]
        AVAILABLE_EMOTIONS = config["emotions"]["available"]
        DEFAULT_EMOTION = config["emotions"]["default"]
        AUTO_RESET_MINUTES = config["emotions"]["auto_reset_minutes"]
        VISION_MOCK_IMAGE_PATH = Path(__file__).parent.parent / config["vision"]["mock_image_path"]

        # TTS settings (Fish Audio)
        TTS_CONFIG = config.get("tts", {})
        TTS_URL = TTS_CONFIG.get("url", "http://localhost:8250")
        TTS_ENABLED = TTS_CONFIG.get("enabled", True)
        TTS_REFERENCE_ID = TTS_CONFIG.get("reference_id", "dutch2")
        TTS_TEMPERATURE = TTS_CONFIG.get("temperature", 0.2)
        TTS_TOP_P = TTS_CONFIG.get("top_p", 0.5)
        TTS_FORMAT = TTS_CONFIG.get("format", "wav")
        TTS_STREAMING = TTS_CONFIG.get("streaming", False)

        return {"status": "ok", "message": "Config herladen", "model": OLLAMA_MODEL, "tts_enabled": TTS_ENABLED, "tts_streaming": TTS_STREAMING}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config reload failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    host = config.get("orchestrator", {}).get("host", "0.0.0.0")
    port = config.get("orchestrator", {}).get("port", 8200)
    uvicorn.run(app, host=host, port=port)
