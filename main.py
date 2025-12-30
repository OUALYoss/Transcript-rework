import json
from pathlib import Path
from dotenv import load_dotenv

from src.ingestion.ingestion import load, save
from src.pipeline import run
from src.steps.filler_removal import remove_fillers
from src.steps.repetition_removal import remove_repetitions
from src.steps.llm_correction import llm_correct
from src.evluation.metrique import wer, glossary_precision, llm_judge

load_dotenv()

STEPS = [remove_fillers, remove_repetitions, llm_correct]


def save_json(data: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def process_file(input_path: str, output_path: str, trace_path: str) -> tuple:
    """Traite un fichier et retourne (original, corrigé)"""
    transcript = load(input_path)
    result, trace = run(transcript, STEPS)
    save(result, output_path)
    save_json(trace.to_dict(), trace_path)
    print(f"{Path(input_path).name} → {trace.summary()['total_changes']} modifications")
    return transcript, result


def evaluate(original, corrected) -> dict:
    """Évalue un transcript corrigé."""
    glossary = original.context.glossary if original.context else []

    orig_text = " ".join(m.content for m in original.messages)
    corr_text = " ".join(m.content for m in corrected.messages)

    return {
        "transcript_id": original.transcript_id,
        "wer": wer(orig_text, corr_text),
        "glossary_precision": glossary_precision(corr_text, glossary),
        "llm_judge": llm_judge(orig_text, corr_text),
    }


def main(
    input_dir: str = "data/raw",
    output_dir: str = "data/processed",
    trace_dir: str = "data/trace",
) -> None:
    """Traite et évalue tous les fichiers."""
    evaluations = []

    for file in Path(input_dir).glob("*.json"):
        output_path = Path(output_dir) / file.name
        trace_path = Path(trace_dir) / f"{file.stem}_trace.json"

        original, corrected = process_file(str(file), str(output_path), str(trace_path))

        metrics = evaluate(original, corrected)
        evaluations.append(metrics)

        print(
            f"   WER: {metrics['wer']:.2%} | Glossaire: {metrics['glossary_precision']:.2%}"
        )
        if "average" in metrics["llm_judge"]:
            print(f"   LLM Judge: {metrics['llm_judge']['average']}/10")

    save_json(evaluations, f"{trace_dir}/evaluation_summary.json")


if __name__ == "__main__":
    main()
    print("done")
