# src/io/llm_client.py
from __future__ import annotations

import os
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from src.utils.utils_logger import get_logger

logger = get_logger()


def _get_session(timeout_s: float = 12.0) -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.request = _with_timeout(session.request, timeout_s)  # type: ignore
    return session


def _with_timeout(fn, timeout_s: float):
    def _wrapped(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout_s)
        return fn(method, url, **kwargs)
    return _wrapped


def suggest_user_hint(user_text: str) -> str:
    """
    Ruft das LLM (synchron) auf, um eine kurze, konkrete Hilfenachricht zu generieren.
    Diese Funktion wird vom Use-Case via asyncio.to_thread(...) aufgerufen.
    """
    logger.debug("llm_client.suggest_user_hint user_text=%r", user_text)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY fehlt – nutze Fallback-Hinweis.")
        return (
            "Ich konnte keine Koordinaten erkennen. Bitte sende sie als Dezimalgrad, "
            "z. B. 49.123, 8.456"
        )

    # Beispiel für ein generisches Backend (pseudocode); passe bei dir konkret an:
    try:
        session = _get_session()
        resp = session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Formuliere kurz und hilfreich auf Deutsch, wie man Koordinaten im Format "
                            "'lat, lon' sendet. Gib ein einziges Beispiel."
                        ),
                    },
                    {"role": "user", "content": user_text},
                ],
                "temperature": 0.2,
                "max_tokens": 120,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        return content or "Bitte sende Koordinaten als Dezimalgrad, z. B. 49.123, 8.456"
    except Exception as e:
        logger.exception("LLM request failed: %s", e)
        return "Ich konnte das nicht verstehen. Bitte sende Koordinaten wie 49.123, 8.456."
