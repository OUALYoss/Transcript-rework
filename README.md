# Transcript Rework

Pipeline de correction automatique de transcripts téléphoniques pour Omogen.

## Le problème

Les outils de transcription automatique (Whisper, Gladia, AssemblyAI...) génèrent des transcripts avec pas mal d'erreurs : fillers ("euh", "ben"), répétitions ("chez chez"), termes techniques mal transcrits ("postgre sql" au lieu de "PostgreSQL"), ponctuation absente ou incorrecte. Ces erreurs rendent les transcripts difficiles à lire et à exploiter.

## La solution

Un pipeline en 3 étapes qui nettoie les transcripts automatiquement, avec traçabilité complète et évaluation des corrections.

## Architecture du pipeline

![Pipeline Schema](docs/Mermaid Chart - Create complex, visualdiagrams with text.-2025-12-30-221529.png)

Le pipeline suit un flux linéaire :

**INPUT** → Les transcripts bruts au format JSON contiennent un identifiant, des métadonnées, un contexte métier (glossaire, participants) et la liste des messages avec leurs timestamps.

**PIPELINE** → Trois étapes de correction s'enchaînent. D'abord, le Filler Removal supprime les mots parasites via regex. Ensuite, le Repetition Removal élimine les bégaiements. Enfin, le LLM Correction utilise GPT-4o-mini avec le glossaire du contexte pour corriger orthographe, ponctuation et termes techniques.

**TRACE** → Chaque transformation est enregistrée avec l'état avant/après, permettant une traçabilité complète.

**EVALUATION** → Trois métriques évaluent la qualité : WER (taux d'erreur), précision du glossaire, et un LLM Judge qui note la fidélité et la qualité.

**OUTPUT** → Les transcripts corrigés, les rapports de trace et le résumé d'évaluation sont générés.

## Installation

```bash
git clone https://github.com/OUALYoss/Transcript-rework.git
cd Transcript-rework
pip install -r requirements.txt
```

Créez un fichier `.env` avec vos credentials :

```
OPENAI_API_KEY=sk-votre-clé-ici
MODEL=gpt-4o-mini
```

## Utilisation

```bash
python main.py
```

Les transcripts dans `data/raw/` sont traités. Les résultats vont dans `data/processed/`, les traces dans `data/trace/`.

## Structure du projet

```
transcript-rework/
├── main.py                          # Point d'entrée
├── src/
│   ├── model/
│   │   ├── transcript.py            # Modèles Pydantic
│   │   └── trace.py                 # Traçabilité
│   ├── ingestion/
│   │   └── ingestion.py             # Chargement/sauvegarde JSON
│   ├── pipeline.py                  # Orchestrateur
│   ├── steps/
│   │   ├── filler_removal.py        # Étape 1
│   │   ├── repetition_removal.py    # Étape 2
│   │   └── llm_correction.py        # Étape 3
│   └── evaluation/
│       └── metrique.py              # WER, Glossary, LLM Judge
├── data/
│   ├── raw/                         # Transcripts bruts
│   ├── processed/                   # Transcripts corrigés
│   └── trace/                       # Rapports
└── docs/
    └── pipeline_schema.png          # Schéma architecture
```

## Les 3 étapes du pipeline

**Étape 1 - Filler Removal (regex)** : Supprime les mots parasites du langage oral comme "euh", "ben", "hein", "bah", "donc euh", "tu sais", "voilà", "je veux dire". Ces fillers n'apportent pas d'information et polluent la lecture.

**Étape 2 - Repetition Removal (regex)** : Supprime les bégaiements et répétitions. Les mots simples répétés ("de de" → "de") et les groupes répétés ("en tant que tant que" → "en tant que") sont corrigés.

**Étape 3 - LLM Correction (OpenAI)** : Utilise GPT-4o-mini pour corriger l'orthographe, la ponctuation et appliquer la bonne casse aux termes techniques. Le glossaire du contexte est passé au LLM pour des corrections précises. Le prompt est strict : pas de reformulation, pas d'invention de contenu.

## Exemple avant/après

**Avant :**
```json
"messages": [
      {
        "speaker": "speaker_0",
        "content": "Bonjour monsieur donc euh merci d'avoir postulé chez nous aujourd'hui on va discuter un peu de votre de votre parcours",
        "start_time": 0.0,
        "end_time": 8.2
      },
      {
        "speaker": "speaker_1",
        "content": "Oui bonjour merci de me recevoir donc euh ben j'ai travaillé pendant 3 ans chez chez Techno Corp en tant que tant que développeur back-end",
        "start_time": 8.3,
        "end_time": 18.1
      },
```

**Après :**
```json 
"messages": [
    {
      "speaker": "speaker_0",
      "content": "Bonjour, Monsieur, merci d'avoir postulé chez nous. Aujourd'hui, on va discuter un peu de votre parcours.",
      "start_time": 0.0,
      "end_time": 8.2
    },
    {
      "speaker": "speaker_1",
      "content": "Oui, bonjour, merci de me recevoir. J'ai travaillé pendant 3 ans chez Techno Corp en tant que développeur back-end.",
      "start_time": 8.3,
      "end_time": 18.1
    }
```

## Traçabilité

Chaque transformation est enregistrée dans un rapport JSON détaillé :

```json
{
  "transcript_id": "t1_recrutement",
  "timestamp": "2024-12-30T10:30:00",
  "total_changes": 12,
  "changes": [
    {
      "step": "filler_removal",
      "message_index": 0,
      "before": "Bonjour monsieur donc euh merci...",
      "after": "Bonjour monsieur merci..."
    },
    {
      "step": "repetition_removal",
      "message_index": 1,
      "before": "chez chez Techno Corp",
      "after": "chez Techno Corp"
    }
  ]
}
```

## Métriques d'évaluation

Le projet inclut trois métriques pour évaluer la qualité des corrections.

**WER (Word Error Rate)** mesure la distance entre le texte original et corrigé au niveau des mots. Il utilise la distance de Levenshtein et permet de quantifier l'ampleur des modifications.

**Glossary Precision** calcule le pourcentage de termes techniques du glossaire correctement présents dans le texte corrigé. Un score de 100% indique que tous les termes attendus sont bien formatés.

**LLM Judge** utilise un LLM pour évaluer la qualité sur trois critères notés sur 10 : fidélité (le sens est-il préservé ?), qualité linguistique (orthographe, ponctuation), et termes techniques (sont-ils corrects ?).

Exemple de résultats :
```json
{
  "transcript_id": "t1_recrutement",
  "wer": 0.32,
  "glossary_precision": 1.0,
  "llm_judge": {
    "fidelity": 10,
    "quality": 8,
    "technical": 9,
    "average": 9,
    "comment": "Correction précise, sens préservé."
  }
}
```

## Format des transcripts

Le format d'entrée attendu :

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

Le champ `context.glossary` est essentiel : il indique au LLM quels termes techniques doivent être correctement formatés.

## Challenges en production

**Coût API** : Chaque message génère un appel OpenAI. Pour optimiser, un mode batch pourrait regrouper plusieurs messages par requête.

**Latence** : Environ 500ms par message. Une parallélisation des appels permettrait de traiter les messages simultanément.

**Hallucinations LLM** : Malgré un prompt strict, le risque que le LLM invente du contenu existe. La traçabilité permet de détecter ces cas.

**Contexte limité** : Le LLM voit un message à la fois, pas la conversation entière. Pour des corrections plus cohérentes, passer plusieurs messages ensemble serait bénéfique.

**Langues** : Actuellement optimisé pour le français. Un support multi-langues nécessiterait des adaptations du prompt et des regex.

## Cas limites

Les messages très courts ("Oui", "D'accord") offrent peu de corrections possibles. Le jargon absent du glossaire risque d'être mal corrigé. Les accents régionaux peuvent produire des transcriptions source de mauvaise qualité que le pipeline ne peut pas rattraper. Les chevauchements de parole (diarisation incorrecte) ne sont pas corrigés par ce pipeline.

## Évolutions possibles

**Correction de diarisation via LLM** : Analyser le contexte pour réassigner les speakers mal identifiés.

**Détection d'omissions** : Identifier les phrases incomplètes ou les coupures anormales.

**Mode batch API** : Regrouper les messages pour réduire le nombre d'appels et les coûts.

**ReAct Agent (v2)** : Une approche ReAct permettrait un pipeline plus intelligent avec détection dynamique des erreurs, correction itérative (corrige → vérifie → re-corrige), et réassignation des speakers basée sur le contexte. Trade-offs : plus précis sur cas complexes, mais coût API x3-5 et latence plus élevée.

**Interface web** : Visualiser les corrections avec diff coloré avant/après.

**Pipeline audio complet** : Intégrer Whisper pour un flux audio → texte clean de bout en bout.

## Stack technique

Python 3.12, Pydantic pour la validation, OpenAI API (gpt-4o-mini), python-dotenv pour la configuration, regex pour les étapes heuristiques.
