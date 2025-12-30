import json
from pathlib import Path
from src.model.transcript import Transcript
import os


def normalize_data(data):
    # tri par start_time
    data["messages"] = sorted(data["messages"], key=lambda x: x["start_time"])

    for message in data["messages"]:
        # Enlève les espaces multiples
        message["content"] = " ".join(message["content"].split())

    return data


def load(path: str | Path) -> Transcript:
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return Transcript(**json.load(f))


def save(transcript: Transcript, path: str | Path) -> None:
    """Sauvegarde un transcript."""

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)


def load_all(directory: str | Path) -> list[Transcript]:
    """Charge tous les transcripts d'un dossier."""
    return [load(f) for f in Path(directory).glob("*.json")]
