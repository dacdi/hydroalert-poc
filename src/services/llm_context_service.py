# src/services/llm_context_service.py
"""
Lieferant für kuratierte, stabile Kontexte (optional später: Datei-/RAG-gestützt).
"""
from __future__ import annotations
from typing import Dict
from src.config.llm_prompts import HYDROALERT_CONTEXT_DE

def get_core_context() -> Dict[str, str]:
    return {"de": HYDROALERT_CONTEXT_DE}
