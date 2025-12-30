import re
from src.model.transcript import Transcript
from src.model.trace import TransformationReport


REPETITIONS = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)  # Répétition d'un mot
REPEATED_GROUPS = re.compile(
    r"(\b\w+\s+\w+\b)\s+\1", re.IGNORECASE
)  # Répétition de groupe de mots


def remove_repetitions(
    transcript: Transcript, report: TransformationReport
) -> Transcript:

    for idx, msg in enumerate(transcript.messages):
        before = msg.content
        msg.content = REPETITIONS.sub(r"\1", msg.content)
        msg.content = REPEATED_GROUPS.sub(r"\1", msg.content)
        msg.content = " ".join(msg.content.split())
        report.add("repetition_removal", idx, before, msg.content)

    return transcript
