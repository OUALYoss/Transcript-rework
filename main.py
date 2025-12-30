from pathlib import Path
from dotenv import load_dotenv

from src.ingestion.loader import load, save
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


def process_file(input_path: str, output_path: str) -> None:
    """Traite un fichier."""
    transcript = load(input_path)
    result = run(transcript, STEPS)
    save(result, output_path)
    print(f"{Path(input_path).name} → {Path(output_path).name}")


def process_all(
    input_dir: str = "data/raw", output_dir: str = "data/processed"
) -> None:
    """Traite tous les fichiers."""
    for file in Path(input_dir).glob("*.json"):
        output_path = Path(output_dir) / file.name
        process_file(str(file), str(output_path))


if __name__ == "__main__":
    process_all()
