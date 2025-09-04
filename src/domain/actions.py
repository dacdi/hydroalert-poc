# src/domain/actions.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union

@dataclass(frozen=True)
class SendText:
    text: str

@dataclass(frozen=True)
class SendPhoto:
    path: str
    caption: Optional[str] = None

# ➕ NEU:
@dataclass(frozen=True)
class SendDocument:
    path: str
    filename: Optional[str] = None
    caption: Optional[str] = None

BotAction = Union[SendText, SendPhoto, SendDocument]
