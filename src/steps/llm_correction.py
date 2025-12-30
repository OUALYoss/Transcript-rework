import os
from openai import OpenAI
from src.model.transcript import Transcript
from src.model.trace import TransformationReport


SYSTEM_MESSAGE = """You are a transcript correction assistant.
Your role is to fix transcription errors while preserving the original meaning and structure.

Rules:
- Fix spelling and punctuation errors
- Correct technical terms based on the provided glossary
- Keep the same language (French)
- Do NOT rephrase or paraphrase
- Do NOT add or remove content
- Do NOT translate
- Return ONLY the corrected text, nothing else"""


def correct_with_openai(text: str, glossary: list[str]) -> str:
    """Corrige via API OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("MODEL")

    prompt = f"""Fix ONLY the errors in this French text:
- Spelling and punctuation
- Technical terms (use glossary: {', '.join(glossary)})

Text: "{text}"

Respond in French with ONLY the corrected text."""

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=500,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip().strip('"')


def llm_correct(transcript: Transcript, report: TransformationReport) -> Transcript:
    glossary = transcript.context.glossary if transcript.context else []

    for i, msg in enumerate(transcript.messages):
        before = msg.content
        msg.content = correct_with_openai(msg.content, glossary)
        report.add("llm_correction", i, before, msg.content)
    return transcript
