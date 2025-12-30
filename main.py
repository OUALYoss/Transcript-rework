import json
from pathlib import Path
from dotenv import load_dotenv

from src.ingestion.ingestion import load, save
from src.pipeline import run
from src.steps.filler_removal import remove_fillers
from src.steps.repetition_removal import remove_repetitions
from src.steps.llm_correction import llm_correct

# Charge les variables d'environnement
load_dotenv()

STEPS = [
    remove_fillers,
    remove_repetitions,
    llm_correct,
]


def save_trace(report, path: str) -> None:
    """Sauvegarde le rapport de traçabilité."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)


def process_file(input_path: str, output_path: str, trace_path: str) -> None:
    """Traite un fichier."""
    transcript = load(input_path)
    result, report = run(transcript, STEPS)
    save(result, output_path)
    save_trace(report, trace_path)

    summary = report.summary()
    print(f"{Path(input_path).name} → {summary['total_changes']} modifications")


def process_all(
    input_dir: str = "data/raw",
    output_dir: str = "data/processed",
    trace_dir: str = "data/trace",
) -> None:
    """Traite tous les fichiers."""
    for file in Path(input_dir).glob("*.json"):
        output_path = Path(output_dir) / file.name
        report_path = Path(trace_dir) / f"{file.stem}_trace.json"
        process_file(str(file), str(output_path), str(report_path))


if __name__ == "__main__":
    process_all()
    print("done")
