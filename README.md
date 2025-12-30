# Transcript Rework

Pipeline de correction automatique de transcripts téléphoniques pour Omogen.

## Le problème

Les outils de transcription automatique (Whisper, Gladia, AssemblyAI...) génèrent des transcripts avec pas mal d'erreurs :

- **Fillers** : "euh", "ben", "donc euh" qui polluent le texte
- **Répétitions** : "chez chez", "de de" — typique du langage oral
- **Termes techniques mal transcrits** : "postgre sql" au lieu de "PostgreSQL"
- **Ponctuation absente ou incorrecte**
- **Casse incorrecte** : "api" au lieu de "API"

Ces erreurs rendent les transcripts difficiles à lire et à exploiter.

## La solution

Un pipeline en 3 étapes qui nettoie les transcripts automatiquement :

```
Input (raw) → Fillers → Répétitions → LLM → Output (clean)
```

Chaque étape est indépendante et tracée.

## Installation

```bash
git clone https://github.com/OUALYoss/Transcript-rework.git
cd Transcript-rework
pip install -r requirements.txt
```

Crée un fichier `.env` :
```
OPENAI_API_KEY=sk-ta-clé-ici
MODEL=gpt-4o-mini
```

## Utilisation

```bash
python main.py
```

Les transcripts dans `data/raw/` sont traités et sauvegardés dans `data/processed/`.
Les rapports de traçabilité vont dans `data/reports/`.

## Architecture

```
transcript-rework/
├── main.py                     # Point d'entrée
├── src/
│   ├── model/
│   │   ├── transcript.py       # Modèles Pydantic
│   │   └── trace.py            # Traçabilité
│   ├── ingestion/
│   │   └── ingestion.py        # Chargement/sauvegarde JSON
│   ├── pipeline.py             # Orchestrateur
│   └── steps/
│       ├── filler_removal.py   # Étape 1 : supprime "euh", "ben"...
│       ├── repetition_removal.py # Étape 2 : "chez chez" → "chez"
│       └── llm_correction.py   # Étape 3 : correction via GPT-4o-mini
└── data/
    ├── raw/                    # Transcripts bruts
    ├── processed/              # Transcripts corrigés
    └── reports/                # Rapports de traçabilité
```

## Les 3 étapes du pipeline

### 1. Suppression des fillers (regex)

Supprime les mots parasites du langage oral :
- "euh", "ben", "hein", "bah"
- "donc euh", "et euh", "enfin"
- "tu sais", "voilà", "je veux dire"

### 2. Suppression des répétitions (regex)

Supprime les bégaiements et répétitions :
- Mots simples : "de de" → "de"
- Groupes : "en tant que tant que" → "en tant que"

### 3. Correction LLM (OpenAI)

Utilise GPT-4o-mini pour :
- Corriger l'orthographe et la ponctuation
- Appliquer la bonne casse aux termes techniques (via le glossaire)
- **Sans reformuler ni inventer du contenu**

Le contexte métier (glossaire, domaine) est passé au LLM pour des corrections plus précises.

## Exemple avant/après

**Avant :**
```
Bonjour monsieur donc euh merci d'avoir postulé chez nous
Oui bonjour euh ben j'ai travaillé chez chez Techno Corp
Principalement du python avec postgre sql et redis pour le catching
```

**Après :**
```
Bonjour monsieur, merci d'avoir postulé chez nous.
Oui, bonjour, j'ai travaillé chez Techno Corp.
Principalement du Python avec PostgreSQL et Redis pour le caching.
```

## Traçabilité

Chaque transformation est enregistrée dans un rapport JSON :

```json
{
  "transcript_id": "t1_recrutement",
  "timestamp": "2024-12-30T10:30:00",
  "total_changes": 8,
  "changes": [
    {
      "step": "filler_removal",
      "message_index": 0,
      "before": "Bonjour monsieur donc euh merci...",
      "after": "Bonjour monsieur merci..."
    }
  ]
}
```

## Format des transcripts

**Input :**
```json
{
  "transcript_id": "t1_recrutement",
  "metadata": {
    "duration": 78.4,
    "date": "2024-12-18T10:15:00Z",
    "source": "whisper-large-v3"
  },
  "context": {
    "domain": "recrutement_tech",
    "participants": { "speaker_0": "Recruteur", "speaker_1": "Candidat" },
    "glossary": ["Django", "PostgreSQL", "Redis"]
  },
  "messages": [
    {
      "speaker": "speaker_0",
      "content": "Bonjour donc euh merci d'avoir postulé",
      "start_time": 0.0,
      "end_time": 5.0
    }
  ]
}
```

Le champ `context.glossary` permet au LLM de savoir quels termes techniques corriger.

## Métriques d'évaluation possibles

- **WER (Word Error Rate)** : comparaison avec transcription manuelle de référence
- **Taux de correction** : % de messages modifiés
- **Précision des termes techniques** : % de termes du glossaire correctement appliqués
- **Conservation du sens** : évaluation humaine (pas d'invention)

## Challenges en production

1. **Coût API** : chaque message = 1 appel OpenAI. Batching possible.
2. **Latence** : ~500ms par message. Parallélisation envisageable.
3. **Hallucinations LLM** : le prompt est strict mais risque non nul.
4. **Contexte limité** : le LLM voit un message à la fois, pas la conversation entière.
5. **Langues multiples** : actuellement optimisé pour le français.

## Cas limites

- **Messages très courts** : "Oui", "D'accord" — peu de corrections possibles
- **Jargon inconnu** : termes absents du glossaire mal corrigés
- **Accents régionaux** : transcription source peut être mauvaise
- **Chevauchements** : diarisation incorrecte non corrigée par ce pipeline

## Évolutions possibles

- [ ] Correction de la diarisation via LLM
- [ ] Détection d'omissions (phrases incomplètes)
- [ ] Mode batch pour réduire les appels API
- [ ] Support multi-langues
- [ ] Interface web pour visualiser les corrections
- [ ] Intégration Whisper pour pipeline complet audio → texte clean

## Stack technique

- Python 3.12
- Pydantic (validation)
- OpenAI API (gpt-4o-mini)
- python-dotenv
