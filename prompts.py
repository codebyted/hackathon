# backend/prompts.py

SUBJECT_DETECTION_PROMPT = """
Analyze: "{question}"

Respond ONLY with subject category (lowercase single word):
- mathematics
- science
- geography
- english
- history
- other
"""

SHENG_RULES = """
Standard Swahili → Sheng mapping examples:
- "ni nini" → "ni nini hio"
- "kwa hivyo" → "saa hivyo"
- "mfano" → "kama"
- "kwanza" → "starter pack"
- "halafu" → "then baadaye"
- "hatimaye" → "mwishowe"

Add Sheng phrases:
- Start: "Buda, si ni simple..."
- During: "Unaelewa point?"
- End: "Sawa? Uko tayari kupanda marks!"
"""

def build_explanation_prompt(question: str, subject: str | None = None) -> str:
    return f"""
Act as a Kenyan teacher explaining to a 14-year-old student.

CONTEXT:
- Subject: {subject or "other"}
- Question: {question}

{SHENG_RULES}

EXPLAIN IN THREE VERSIONS:

1. SIMPLE ENGLISH:
   - Use basic vocabulary (CEFR A2 level)
   - Include one relatable Kenyan analogy
   - Break into max 3 steps
   - Use bullet points with emojis

2. KISWAHILI:
   - Use standard Swahili
   - Use clear marking scheme steps
   - Add "Mfano:" with Kenyan context

3. SHENG:
   - Urban, fun tone with Sheng words
   - Must sound like a peer explaining
   - End with motivation

OUTPUT FORMAT (strict JSON):
{{
  "english": "string",
  "kiswahili": "string",
  "sheng": "string",
  "key_points": ["point 1", "point 2"],
  "common_mistakes": "string"
}}
Only output JSON. No explanation outside JSON.
"""