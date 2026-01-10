#!/bin/bash
# Voxtral Transcriptie - alleen spraak naar tekst
# Gebruik: ./test-transcribe.sh <audio.wav>

FILE=$1

if [ -z "$FILE" ]; then
    echo "Gebruik: ./test-transcribe.sh <audio.wav>"
    echo ""
    echo "Voorbeeld:"
    echo "  ./record.sh opname.wav"
    echo "  ./test-transcribe.sh opname.wav"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: Bestand '$FILE' niet gevonden"
    exit 1
fi

echo "Transcriptie van: $FILE"
echo ""

curl -s -X POST http://localhost:8150/v1/audio/transcriptions \
    -H "Content-Type: multipart/form-data" \
    -F "file=@$FILE" \
    -F "model=mistralai/Voxtral-Mini-3B-2507" | jq -r '.text'
