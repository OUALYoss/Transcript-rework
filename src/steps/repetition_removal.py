import re
from src.model.transcript import Transcript


REPETITIONS = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)  # Répétition d'un mot
REPEATED_GROUPS = re.compile(
    r"(\b\w+\s+\w+\b)\s+\1", re.IGNORECASE
)  # Répétition de groupe de mots


def remove_repetitions(transcript: Transcript) -> Transcript:

    for msg in transcript.messages:
        # Supprimer  de mots simples
        msg.content = REPETITIONS.sub(r"\1", msg.content)
        # Supprimer groupes de mots
        msg.content = REPEATED_GROUPS.sub(r"\1", msg.content)
        msg.content = " ".join(msg.content.split())  # Enlève les espaces inutiles

    return transcript
