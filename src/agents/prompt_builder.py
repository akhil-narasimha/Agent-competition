from src.config import CORE_MESSAGES, OBJECTION_CATEGORIES

def build_adherence_prompt() -> str:
    messages = CORE_MESSAGES["LOKELMA"]
    
    message_lines = "\n".join([
        f'{i+1}. "{m["id"]}": {m["label"]} — {m["description"]} (weight: {m["weight"]} pts)'
        for i, m in enumerate(messages)
    ])
    
    score_lines = "\n".join([
        f'  - {m["id"]} = {m["weight"]} points'
        for m in messages
    ])
    
    return f"""You are a Commercial Excellence AI Evaluator for a pharmaceutical company.
Analyze the sales rep's CRM call note and determine which core messages were delivered.
The product is LOKELMA. Core messages to evaluate:
{message_lines}

Scoring weights:
{score_lines}
Total possible score = 100.

CRITICAL RULES:
- Credit the rep only if THEY discussed the concept, not if the HCP raised it unprompted.
- Reps use conversational language. Be generous in your matching.
- Use semantic matching — "fast acting", "quick onset" counts for CM1 even without exact keywords.

Return JSON only:
{{"messages_delivered": ["CM1", "CM3"], "adherence_score": 50}}"""

def build_objection_prompt() -> str:
    categories = "\n".join([
        f'- "{key}": {val["label"]}'
        for key, val in OBJECTION_CATEGORIES.items()
    ])
    
    return f"""You are a Market Access AI Analyst. Extract HCP objections from the call note.
Categories:
{categories}

RULES:
- Only extract objections explicitly stated, not inferred.
- Return empty list if no objections.

Return JSON only:
{{"objections": [{{"type": "affordability", "phrase": "exact quote"}}]}}"""