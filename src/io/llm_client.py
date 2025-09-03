# src/io/llm_client.py
from __future__ import annotations

import json
import os
import logging
from typing import Optional

import requests
from src.utils.utils_logger import get_logger

logger = get_logger()

# Environment configuration
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
TIMEOUT_S = float(os.getenv("LLM_HTTP_TIMEOUT_S", "20"))

FALLBACK_HINT = (
    "Bitte Koordinaten im Format 'lat, lon' mit DezimalPUNKT senden. "
    "Beispiel: 48.1351, 11.5820"
)


def llm_hint_for(user_text: str) -> str:
    """Gibt einen *kurzen* Hilfetext + EIN Beispiel zurück.
    
    Nutzt das LLM, wenn API-Key gesetzt ist. Fällt andernfalls auf einen
    statischen Hinweis zurück. Antwort ist **ein** kurzer Satz + *ein* Beispiel.
    """
    if not API_KEY:
        logger.debug("[LLM] Kein OPENAI_API_KEY gesetzt → Fallback-Hinweis")
        return FALLBACK_HINT

    prompt = (
        "Du hilfst einem Nutzer, Koordinaten im Dezimalgrad-Format korrekt einzugeben.\n"
        "Regeln:\n"
        "- Nur ZWEI Zahlen: erst lat (−90..90), dann lon (−180..180)\n"
        "- DezimalPUNKT (.), kein Dezimalkomma\n"
        "- Trennung mit Komma oder Leerzeichen\n"
        "Gib eine sehr kurze, freundliche Hilfenachricht auf Deutsch und genau EIN gültiges Beispiel.\n"
        "Antworte NUR als JSON-Objekt mit Feldern:\n"
        '{"hint": string, "example": string}\n'
        f"Fehlerhafte Eingabe war: {user_text}"
    )

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "max_tokens": 80,
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        logger.debug("[LLM] POST %s/chat/completions", BASE_URL)
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=body,
            timeout=TIMEOUT_S,
        )
        if resp.status_code == 429:
            logger.warning("[LLM] 429 Too Many Requests → Fallback-Hinweis")
            return FALLBACK_HINT

        resp.raise_for_status()
        data = resp.json()
        content: Optional[str] = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )
        if not content:
            logger.debug("[LLM] Leere Antwort → Fallback-Hinweis")
            return FALLBACK_HINT

        j = json.loads(content)
        hint = (j.get("hint") or "").strip()
        example = (j.get("example") or "").strip()

        if hint and example:
            out = f"{hint} Beispiel: {example}"
            logger.debug("[LLM] Parsed hint: %s", out)
            return out

        logger.debug("[LLM] Ungültiges JSON-Feldformat → Fallback-Hinweis")
        return FALLBACK_HINT

    except Exception as exc:
        logger.warning("[LLM] Fehler: %s → Fallback-Hinweis", exc)
        return FALLBACK_HINT
