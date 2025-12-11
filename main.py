# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import json
import httpx

from .prompts import SUBJECT_DETECTION_PROMPT, build_explanation_prompt
from .cache import get_from_cache, store_in_cache
from .ocr import extract_text_from_base64

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1-mini"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


class ExplainRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None
    subject: Optional[str] = None


class ExplainResponse(BaseModel):
    english: str
    kiswahili: str
    sheng: str
    key_points: list[str]
    common_mistakes: str
    subject_detected: str


async def call_llm(system_prompt: str, user_prompt: str) -> str:
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.post(OPENAI_URL, json=data, headers=headers)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


@app.post("/api/explain", response_model=ExplainResponse)
async def explain(req: ExplainRequest):

    # 1. OCR fallback
    if req.image_base64 and not req.text:
        ocr = extract_text_from_base64(req.image_base64)
        if not ocr["success"]:
            raise HTTPException(status_code=400, detail="OCR failed.")
        req.text = ocr["text"]

    if not req.text:
        raise HTTPException(status_code=400, detail="No text provided.")

    # 2. Cache check
    cached = get_from_cache(req.text)
    if cached:
        return cached

    # 3. Detect subject if not provided
    subject = req.subject
    if subject is None:
        subject = (
            await call_llm(
                "You are a classifier. One-word answers only.",
                SUBJECT_DETECTION_PROMPT.format(question=req.text),
            )
        ).strip().split()[0].lower()

    # 4. Build prompt
    prompt = build_explanation_prompt(req.text, subject)

    # 5. Get explanation JSON
    raw = await call_llm("You are a JSON-only Kenyan tutor.", prompt)

    try:
        parsed = json.loads(raw)
    except:
        raise HTTPException(status_code=500, detail="Invalid JSON from LLM.")

    result = {
        "english": parsed.get("english", ""),
        "kiswahili": parsed.get("kiswahili", ""),
        "sheng": parsed.get("sheng", ""),
        "key_points": parsed.get("key_points", []),
        "common_mistakes": parsed.get("common_mistakes", ""),
        "subject_detected": subject,
    }

    store_in_cache(req.text, result)
    return result