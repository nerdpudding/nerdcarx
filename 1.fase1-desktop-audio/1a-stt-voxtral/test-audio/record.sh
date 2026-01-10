#!/bin/bash
# Neem audio op tot Ctrl-C
# Gebruik: ./record.sh [bestandsnaam]

OUTPUT=${1:-recording.wav}
DEVICE=${RECORD_DEVICE:-hw:5,0}

echo "Opnemen naar: $OUTPUT"
echo "Microfoon: $DEVICE"
echo ""
echo "Druk Ctrl-C om te stoppen..."
echo ""

# Trap Ctrl-C om netjes af te sluiten
trap "echo ''; echo 'Opname gestopt.'; exit 0" INT

arecord -D "$DEVICE" -f S16_LE -r 44100 -c 1 -t wav "$OUTPUT"
