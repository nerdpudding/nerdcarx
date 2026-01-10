# VAD Desktop - Voice Activity Detection

Hands-free testing van de audio pipeline met Silero VAD.

## Quick Start

```bash
# 1. Activeer environment
conda activate nerdcarx-vad

# 2. Zorg dat Voxtral draait
docker compose -f ../1a-stt-voxtral/docker/docker-compose.yml up -d

# 3. Start VAD listener of conversation
python vad_listen.py           # Alleen transcriptie
python vad_conversation.py     # Heen-en-weer gesprek
```

## Scripts

### vad_listen.py - Transcriptie / Single Q&A

Spreek, krijg transcriptie of antwoord terug. Geen conversation history.

```bash
python vad_listen.py           # Transcriptie mode
python vad_listen.py --chat    # Chat mode (single Q&A)
```

### vad_conversation.py - Volledige Conversatie

Heen-en-weer gesprek met conversation history. AI onthoudt context.

```bash
python vad_conversation.py
python vad_conversation.py --system-prompt "Je bent een grappige robot."
```

Stop de conversatie met "stop nu het gesprek" of Ctrl+C.

### Opties

```bash
python vad_listen.py --help

  --chat                 Chat mode: Voxtral beantwoordt vragen
  --silence-duration     Stilte duur voor einde detectie (default: 1.5s)
  --device               Audio device ID (skip selectie menu)
```

## Voorbeeld Output

```
🔄 VAD model laden...
✅ VAD model geladen

🎤 Beschikbare Audio Input Devices:
============================================================
   4: USB2.0 Device: Audio (hw:1,0) (DEFAULT)
   11: Razer Seiren Mini: USB Audio (hw:4,0)
============================================================
Selecteer device ID (default: 4): 11
✅ Geselecteerd: Razer Seiren Mini: USB Audio (hw:4,0)

🎙️ VAD Listener gestart (TRANSCRIPTIE mode)
============================================================
Instructies:
  • Spreek wanneer je klaar bent - VAD detecteert automatisch
  • Stilte van 1.5s beëindigt opname
  • Ctrl+C om te stoppen
============================================================

🎧 Luisteren... (spreek wanneer klaar)
🔴 Spraak gedetecteerd - opname gestart
⏸️ Stilte gedetecteerd - opname gestopt
📊 Opname: 2.3s
📤 Verzenden naar Voxtral...
📝 Transcriptie: Wat is de hoofdstad van Frankrijk?

🎧 Luisteren... (spreek wanneer klaar)
```

## Environment Setup

Als je de environment nog niet hebt:

```bash
conda create -n nerdcarx-vad python=3.12 -y
conda activate nerdcarx-vad
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install silero-vad pyaudio requests
```

## Troubleshooting

### Voxtral niet bereikbaar

```
❌ Kan niet verbinden met Voxtral. Draait de container?
```

Start de Voxtral container:
```bash
cd ../1a-stt-voxtral/docker
docker compose up -d
```

### Geen audio devices

Controleer of je microfoon is aangesloten en herkend wordt:
```bash
arecord -l
```
