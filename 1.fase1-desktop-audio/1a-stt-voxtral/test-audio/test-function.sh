#!/bin/bash
# Voxtral Function Calling Test
# Gebruik: ./test-function.sh <audio.wav>
#
# Test of Voxtral function calls kan genereren vanuit spraak.
# Spreek bijv: "Toon een blije emotie" of "Laat een verdrietig gezicht zien"

FILE=$1

if [ -z "$FILE" ]; then
    echo "Gebruik: ./test-function.sh <audio.wav>"
    echo ""
    echo "Voorbeeld:"
    echo "  ./record.sh commando.wav"
    echo "  # Spreek: 'Toon een blije emotie'"
    echo "  ./test-function.sh commando.wav"
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
  "messages": [
    {
      "role": "system",
      "content": "Je bent een robot assistent. Gebruik de beschikbare tools om commando's uit te voeren. Als de gebruiker vraagt om een emotie te tonen, gebruik dan de show_emotion functie."
    },
    {
      "role": "user",
      "content": [
        {"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64,$B64"}}
      ]
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "show_emotion",
        "description": "Toon een emotie op het OLED scherm van de robot",
        "parameters": {
          "type": "object",
          "properties": {
            "emotion": {
              "type": "string",
              "enum": ["happy", "sad", "angry", "surprised", "neutral"],
              "description": "De emotie om te tonen"
            }
          },
          "required": ["emotion"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
JSONEOF

echo "Response:"
curl -s -X POST http://localhost:8150/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/request.json | jq '.choices[0].message'
