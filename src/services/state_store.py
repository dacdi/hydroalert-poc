# src/services/state_store.py
from __future__ import annotations

from typing import Dict, Optional, Tuple
from src.utils.utils_logger import get_logger

logger = get_logger()

_pending_by_chat: Dict[int, Tuple[float, float]] = {}


def set_pending(chat_id: int, lat: float, lon: float) -> None:
    logger.debug("state_store set_pending chat_id=%s lat=%s lon=%s", chat_id, lat, lon)
    _pending_by_chat[chat_id] = (lat, lon)


def get_pending(chat_id: int) -> Optional[Tuple[float, float]]:
    value = _pending_by_chat.get(chat_id)
    logger.debug("state_store get_pending chat_id=%s -> %r", chat_id, value)
    return value


def clear_pending(chat_id: int) -> None:
    logger.debug("state_store clear_pending chat_id=%s", chat_id)
    _pending_by_chat.pop(chat_id, None)
