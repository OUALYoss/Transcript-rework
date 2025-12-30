from typing import Callable
from src.model.transcript import Transcript

# Type pour une étape
Step = Callable[[Transcript], Transcript]


def run(transcript: Transcript, steps: list[Step]) -> Transcript:
    """Exécute le pipeline."""
    result = transcript.model_copy(deep=True)
    for step in steps:
        result = step(result)
    return result
