import re
from src.models.transcript import Transcript

FILLERS = re.compile(
    r"\b(euh|ben|hein|bah|donc euh|et euh|enfin|quoi|tu sais|voilà|je veux dire|ouais|hum|ah)\b",
    re.IGNORECASE,
)


def remove_fillers(transcript: Transcript) -> Transcript:
    """Supprime les mots de remplissage."""
    for msg in transcript.messages:
        cleaned = FILLERS.sub("", msg.content)
        msg.content = " ".join(cleaned.split())  # Normalise espaces
    return transcript
