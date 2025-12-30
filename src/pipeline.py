from typing import Callable
from src.model.transcript import Transcript
from src.model.trace import TransformationReport

# Type: step(transcript, report) -> transcript
Step = Callable[[Transcript, TransformationReport], Transcript]


def run(
    transcript: Transcript, steps: list[Step]
) -> tuple[Transcript, TransformationReport]:

    result = transcript.model_copy(deep=True)
    report = TransformationReport(transcript_id=transcript.transcript_id)

    for step in steps:
        result = step(result, report)
    return result, report

