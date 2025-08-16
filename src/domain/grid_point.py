# src/domain/grid_point.py
from dataclasses import dataclass

@dataclass(frozen=True)
class GridPoint:
    lat: float
    lon: float
