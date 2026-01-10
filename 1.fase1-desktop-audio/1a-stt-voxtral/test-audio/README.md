# Test Audio Scripts

Test scripts voor Voxtral STT.

> **Let op:** Scripts uitvoeren met `./` prefix, bijv. `./record.sh` (niet `record.sh`)

## Vereisten

- Voxtral container draait op `localhost:8150`
- `jq` geinstalleerd (`sudo apt install jq`)

## Scripts

### record.sh - Opnemen

Neem audio op tot je Ctrl-C drukt.

```bash
./record.sh vraag.wav
# Spreek je vraag in...
# Druk Ctrl-C om te stoppen
```

Andere microfoon: `RECORD_DEVICE=hw:3,0 ./record.sh vraag.wav`

### test-transcribe.sh - Alleen Transcriptie

Spraak naar tekst, geen antwoord.

```bash
./test-transcribe.sh vraag.wav
# Output: "Wat is de hoofdstad van Frankrijk?"
```

### test-chat.sh - Voice Assistant

Voxtral beantwoordt je vraag direct (volledige LLM).

```bash
./test-chat.sh vraag.wav
# Output: "De hoofdstad van Frankrijk is Parijs."

# Met custom systeem prompt
./test-chat.sh vraag.wav "Je bent een grappige robot."
```

## Voorbeeld: Getest en Werkend

```bash
# 1. Opnemen
./record.sh vraag.wav
# Ingesproken: "Kan je mij vertellen wat de hoofdstad van Frankrijk is?
#              En ik wil ook de hoofdstad van Nederland weten."

# 2. Transcriptie
./test-transcribe.sh vraag.wav
# Output: "Zeg, kan je mij vertellen wat is de hoofdstad van Frankrijk?
#          En ik wil ook wel de hoofdstad van Nederland weten eigenlijk."

# 3. Chat (antwoord)
./test-chat.sh vraag.wav
# Output: "De hoofdstad van Frankrijk is Parijs en de hoofdstad van
#          Nederland is Amsterdam."
```

### test-function.sh - Function Calling

Test function calling vanuit spraak (voor robot acties).

```bash
./record.sh commando.wav
# Spreek: "Laat me een blij gezichtje zien"

./test-function.sh commando.wav
# Output: {"emotion": "happy"}
```

## Voorbeeld: Function Calling Getest en Werkend

```bash
# 1. Opnemen
./record.sh commando.wav
# Ingesproken: "Laat me eens een blij gezichtje zien."

# 2. Transcriptie check
./test-transcribe.sh commando.wav
# Output: "Laat me eens een blij gezichtje zien."

# 3. Function call
./test-function.sh commando.wav
# Output: [TOOL_CALLS][{"emotion": "happy"}]
```

## Microfoon

```bash
# Zoek je microfoon
arecord -l

# Pas device aan (default: hw:5,0)
RECORD_DEVICE=hw:3,0 ./record.sh test.wav
```

## Parameters

| Script | Temperature | Doel |
|--------|-------------|------|
| test-transcribe.sh | 0.0 | Exacte transcriptie |
| test-chat.sh | 0.2 | Antwoorden genereren |
| test-function.sh | 0.2 | Function calling |

Bron: [HuggingFace Model Card](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507)
