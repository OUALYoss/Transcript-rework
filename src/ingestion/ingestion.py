import json
import os


def load_json(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def normalize_data(data):
    # tri par start_time
    data["messages"] = sorted(data["messages"], key=lambda x: x["start_time"])

    for message in data["messages"]:
        # Enlève les espaces multiples
        message["content"] = " ".join(message["content"].split())

    return data


if __name__ == "__main__":
    file_path = "src/data/raw/t1_recrutement.json"
    transcript_data = load_json(file_path)
    # Normaliser les données
    normalized_data = normalize_data(transcript_data)
