# src/io/llm_client.py
from __future__ import annotations
# src/io/llm_client.py

import os
from typing import Dict, List

import requests
from requests.adapters import HTTPAdapter, Retry

from src.utils.utils_logger import get_logger
from src.services.llm_context_service import get_core_context
from src.config.llm_prompts import (
    PROMPT_HINT_COORDS_DE,
    PROMPT_HYDROALERT_EXPLAIN_DE,
)

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


def _chat_complete(messages: List[Dict[str, str]], *, max_tokens: int = 240, temperature: float = 0.2) -> str:
    """Kleiner Wrapper um das Chat-API; modell über ENV konfigurierbar."""
    logger.debug("llm_client._chat_complete start messages_count=%d", len(messages))
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY fehlt – nutze Fallback.")
        return "OPENAI_API_KEY fehlt. Bitte sende Koordinaten wie 49.123, 8.456."

    try:
        session = _get_session()
        resp = session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        logger.debug("llm_client._chat_complete ok chars=%d", len(content))
        return content or "Bitte sende Koordinaten als Dezimalgrad, z. B. 49.123, 8.456"
    except Exception as e:
        logger.exception("LLM request failed: %s", e)
        return "Ich konnte das nicht verarbeiten. Bitte nutze das Format 49.123, 8.456."


def suggest_user_hint(user_text: str) -> str:
    """
    Kurzer Hilfetext zu 'lat, lon' – nutzt kuratierten Kontext.
    Wird vom Use-Case via asyncio.to_thread(...) aufgerufen.
    """
    logger.debug("llm_client.suggest_user_hint user_text=%r", user_text)
    context = get_core_context()["de"]
    system = PROMPT_HINT_COORDS_DE.format(context=context)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]
    return _chat_complete(messages, max_tokens=120, temperature=0.2)


def explain_hydroalert(user_text: str = "Kurzer Überblick zu HydroAlert") -> str:
    """
    Prägnanter Überblick inkl. Dummy-Test- und Koordinatenhinweis (FAQ/Help).
    """
    logger.debug("llm_client.explain_hydroalert user_text=%r", user_text)
    context = get_core_context()["de"]
    system = PROMPT_HYDROALERT_EXPLAIN_DE.format(context=context, user_text=user_text)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]
    return _chat_complete(messages, max_tokens=160, temperature=0.2)
