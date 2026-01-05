import os
import json
from openai import OpenAI


def wer(reference: str, hypothesis: str) -> float:
    """Calcule le Word Error Rate (WER) entre deux textes.
    
    Le WER mesure la distance de Levenshtein au niveau des mots,
    normalisée par la longueur du texte de référence. Plus le score
    est bas, plus les textes sont similaires.
    
    Args:
        reference: Texte original (référence).
        hypothesis: Texte corrigé (hypothèse à évaluer).
    
    Returns:
        Score WER entre 0.0 (identique) et >1.0 (très différent).
        Retourne 0.0 si la référence est vide.
    """
    ref = reference.lower().split()
    hyp = hypothesis.lower().split()

    if len(ref) == 0:
        return 0.0

    # Matrice de distance
    d = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
    for i in range(len(ref) + 1):
        d[i][0] = i
    for j in range(len(hyp) + 1):
        d[0][j] = j

    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)

    return d[len(ref)][len(hyp)] / len(ref)


def glossary_precision(text: str, glossary: list[str]) -> float:
    """Calcule le pourcentage de termes du glossaire présents dans le texte.
    
    Vérifie la présence exacte (case-sensitive) de chaque terme
    du glossaire dans le texte corrigé.
    
    Args:
        text: Texte dans lequel rechercher les termes.
        glossary: Liste des termes techniques attendus.
    
    Returns:
        Score entre 0.0 (aucun terme trouvé) et 1.0 (tous les termes présents).
        Retourne 1.0 si le glossaire est vide.
    """
    if not glossary:
        return 1.0
    found = sum(1 for term in glossary if term in text)
    return found / len(glossary)


def llm_judge(original: str, corrected: str) -> dict:
    """LLM as judge 
    Évalue la qualité d'une correction via un LLM (GPT-4o-mini).
    
    Utilise le paradigme "LLM as a Judge" pour noter la correction
    sur trois critères : fidélité au sens original, qualité linguistique,
    et précision des termes techniques.
    
    Args:
        original: Texte avant correction.
        corrected: Texte après correction.
    
    Returns:
        Dictionnaire contenant les scores et commentaires :
        {
            "fidelity": int,    # Note /10 - sens préservé
            "quality": int,     # Note /10 - orthographe, ponctuation
            "technical": int,   # Note /10 - termes techniques
            "average": float,   # Moyenne des trois notes
            "comment": str      # Commentaire en français
        }
    
    
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("MODEL", "gpt-4o-mini")
    SYSTEM_MESSAGE = """You are a transcript correction evaluator.
Your role is to assess the quality of transcript corrections.

Rules:
- Score each criterion from 0 to 10
- Be objective and precise
- Respond ONLY in valid JSON format
- Comment in French, keep it brief"""

    prompt = f"""Évalue cette correction (notes /10):
1. Fidélité (sens préservé)
2. Qualité (orthographe, ponctuation)
3. Termes techniques

ORIGINAL: "{original}"
CORRIGÉ: "{corrected}"

Réponds en JSON: {{"fidelity": X, "quality": X, "technical": X, "average": X, "comment": "..."}}"""

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"): # ``json
        content = content.split("\n", 1)[1].rsplit("```", 1)[0]

    return json.loads(content)
