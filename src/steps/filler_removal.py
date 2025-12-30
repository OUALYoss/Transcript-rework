import re
from src.model.transcript import Transcript
from src.model.trace import TransformationReport


FILLERS = re.compile(
    r"\b(euh|ben|hein|bah|donc euh|et euh|enfin|quoi|tu sais|voilà|je veux dire|ouais|hum|ah)\b",
    re.IGNORECASE,
)


def remove_fillers(transcript: Transcript, report: TransformationReport) -> Transcript:
    for i, msg in enumerate(transcript.messages):
        before = msg.content
        cleaned = FILLERS.sub("", before)
        msg.content = " ".join(cleaned.split())  # Normalise espaces
        report.add("filler_removal", i, before, msg.content)
    return transcript
