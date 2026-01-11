# VAD Desktop - Voice Activity Detection

Hands-free gesprekken met de volledige AI pipeline.

**Flow:**
```
[Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral LLM] → response
                                      ↓
                            + Vision (foto meesturen)
                            + Function calling (emoties)
```

## Quick Start

```bash
# 1. Activeer environment
conda activate nerdcarx-vad

# 2. Zorg dat alle services draaien (zie ../FASE1-PLAN.md)

# 3. Start VAD conversation
python vad_conversation.py
```

## Scripts

### vad_listen.py - Transcriptie only

Spreek, krijg transcriptie terug. Direct naar Voxtral, geen orchestrator.

```bash
python vad_listen.py           # Transcriptie mode
python vad_listen.py --chat    # Chat mode (Voxtral beantwoordt)
```

### vad_conversation.py - Volledige Pipeline

Gesprek via de complete chain met vision en function calling.

```bash
python vad_conversation.py
python vad_conversation.py --image /pad/naar/foto.jpg
python vad_conversation.py --no-image
```

## Opties

```
--system-prompt    Custom system prompt
--silence-duration Stilte duur voor einde (default: 1.5s)
--device           Audio device ID
--image            Pad naar image (default: test_foto.jpg)
--no-image         Geen vision
```

## Vision

Standaard wordt `test_foto.jpg` meegestuurd bij elke request.
Dit simuleert de robot camera.

- Bij vragen als "wat zie je?" beschrijft de LLM de foto
- Bij andere vragen negeert de LLM de foto (meestal)

## Function Calling

De LLM kan `show_emotion` aanroepen. Dit wordt getoond als:
```
🎭 [EMOTIE] happy 😊
```

Later: dit stuurt naar het OLED display op de robot.

## Voorbeeld Output

```
📷 Image geladen: test_foto.jpg
🔄 Services checken...
✅ Orchestrator en Voxtral bereikbaar
✅ VAD model geladen

🎙️ VAD Conversation gestart
============================================================
Flow: [Mic] → [VAD] → [Voxtral STT] → [Orchestrator] → [Ministral]
Conversation ID: vad-abc12345
Vision: 📷 Enabled
============================================================

[Turn 1]
🎧 Luisteren... (spreek wanneer klaar)
🔴 Spraak gedetecteerd...
📝 Transcriberen (Voxtral)...
👤 Jij: Wat zie je voor je?
🤔 Denken (Ministral)... 📷
🎭 [EMOTIE] happy 😊
🤖 NerdCarX: Ik zie twee golden retriever puppies in een bloemenveld.
```

## Environment Setup

```bash
conda create -n nerdcarx-vad python=3.12 -y
conda activate nerdcarx-vad
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install silero-vad pyaudio requests
```

## Stop Commando

Zeg "stop nu het gesprek" of druk Ctrl+C.
