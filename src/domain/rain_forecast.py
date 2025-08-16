# src/domain/rain_forecast.py
from dataclasses import dataclass
from typing import List
from .grid_point import GridPoint

@dataclass
class RainForecast:
    point: GridPoint
    hourly_values: List[float]  # Länge 24, mm/h
