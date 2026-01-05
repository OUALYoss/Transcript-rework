import json
from pathlib import Path
from src.model.transcript import Transcript
import os


def load(path: str | Path) -> Transcript:
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return Transcript(**json.load(f))


def save(transcript: Transcript, path: str | Path) -> None:

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)


def load_all(directory: str | Path) -> list[Transcript]:
    return [load(f) for f in Path(directory).glob("*.json")] #retourne tous les fichiers qui correspondent à un motif
