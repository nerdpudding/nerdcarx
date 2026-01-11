#!/bin/bash
# Voxtral Chat - spraak naar antwoord (voice assistant)
# Gebruik: ./test-chat.sh <audio.wav> [systeem prompt]

FILE=$1
SYSTEM_PROMPT=${2:-"Je bent een behulpzame AI assistent. Beantwoord de vraag van de gebruiker kort en duidelijk in het Nederlands."}

if [ -z "$FILE" ]; then
    echo "Gebruik: ./test-chat.sh <audio.wav> [systeem prompt]"
    echo ""
    echo "Voorbeelden:"
    echo "  ./record.sh vraag.wav"
    echo "  ./test-chat.sh vraag.wav"
    echo "  ./test-chat.sh vraag.wav \"Je bent een grappige robot.\""
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: Bestand '$FILE' niet gevonden"
    exit 1
fi

echo "Audio: $FILE"
echo ""

B64=$(base64 -w0 "$FILE")

cat > /tmp/request.json << JSONEOF
{
  "model": "mistralai/Voxtral-Mini-3B-2507",
  "temperature": 0.2,
  "top_p": 0.95,
  "max_tokens": 500,
  "messages": [
    {
      "role": "system",
      "content": "$SYSTEM_PROMPT"
    },
    {
      "role": "user",
      "content": [
        {"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64,$B64"}}
      ]
    }
  ]
}
JSONEOF

curl -s -X POST http://localhost:8150/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/request.json | jq -r '.choices[0].message.content'
