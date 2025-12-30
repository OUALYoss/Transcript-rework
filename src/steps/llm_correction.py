import os
from openai import OpenAI
from src.model.transcript import Transcript


def correct_with_openai(text: str, glossary: list[str]) -> str:
    """Corrige via API OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("Model")

    prompt = f"""Corrige UNIQUEMENT les erreurs dans ce texte:
- Orthographe et ponctuation
- Termes techniques: {', '.join(glossary)}

NE PAS reformuler ou ajouter du contenu.

Texte: "{text}"

Réponds UNIQUEMENT avec le texte corrigé, rien d'autre."""

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip().strip('"')


def llm_correct(transcript: Transcript) -> Transcript:

    glossary = transcript.context.glossary if transcript.context else []

    for msg in transcript.messages:
        msg.content = correct_with_openai(msg.content, glossary)

    return transcript
