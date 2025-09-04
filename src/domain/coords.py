# src/domain/coords.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Coords:
    lat: float
    lon: float
