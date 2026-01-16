"""
Text normalization voor TTS preprocessing.

Functies:
- Acroniemen naar Nederlandse fonetiek (API → aa-pee-ie)
- Getallen naar woorden (150 → honderdvijftig)
- Haakjes → komma's
- Engelse woorden → Nederlands-klinkend
"""
import re

from num2words import num2words


# Nederlandse fonetische uitspraak voor letters
NL_LETTER_SOUNDS = {
    'A': 'aa', 'B': 'bee', 'C': 'see', 'D': 'dee', 'E': 'ee',
    'F': 'ef', 'G': 'zjee', 'H': 'haa', 'I': 'ie', 'J': 'jee',
    'K': 'kaa', 'L': 'el', 'M': 'em', 'N': 'en', 'O': 'oo',
    'P': 'pee', 'Q': 'kuu', 'R': 'er', 'S': 'es', 'T': 'tee',
    'U': 'uu', 'V': 'vee', 'W': 'wee', 'X': 'iks', 'Y': 'ei',
    'Z': 'zet'
}

# Woorden die NIET fonetisch gespeld moeten worden
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

    Transformaties:
    1. Haakjes → komma's
    2. Acroniemen → fonetische spelling
    3. Engelse woorden → Nederlands-klinkend
    4. Getallen → Nederlandse woorden

    Args:
        text: Ruwe tekst

    Returns:
        Genormaliseerde tekst voor TTS
    """
    # 1. HAAKJES: eerste ( wordt ", ", daarna haakjes verwijderen
    text = re.sub(r'\s*\(', ', ', text, count=1)
    text = re.sub(r'[()]', '', text)

    # 2. ACRONIEMEN: letter-voor-letter uitspreken
    def spell_acronym(match):
        acronym = match.group(0)
        if acronym in SKIP_ACRONYMS:
            return acronym
        return '-'.join(NL_LETTER_SOUNDS.get(c, c) for c in acronym)

    text = re.sub(r'\b[A-Z]{2,}\b', spell_acronym, text)

    # 3. SPECIFIEKE WOORDEN
    for pattern, replacement in WORD_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 4. GETALLEN: naar Nederlandse woorden
    def replace_number(match):
        num_str = match.group(0)
        try:
            if '.' in num_str:
                parts = num_str.split('.')
                whole = num2words(int(parts[0]), lang='nl')
                decimal = ' '.join(num2words(int(d), lang='nl') for d in parts[1])
                return f"{whole} komma {decimal}"
            return num2words(int(num_str), lang='nl')
        except (ValueError, OverflowError):
            return num_str

    text = re.sub(r'\b\d+(?:\.\d+)?\b', replace_number, text)

    return text


def split_into_sentences(text: str) -> list[str]:
    """
    Split tekst in zinnen voor pseudo-streaming TTS.

    Args:
        text: Tekst om te splitten

    Returns:
        Lijst van zinnen (non-empty)
    """
    # Split op . ! ? gevolgd door spatie of einde string
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Filter lege zinnen
    return [s.strip() for s in sentences if s.strip()]
