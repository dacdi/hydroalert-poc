# src/analysis/grid_ops.py
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Iterable

def generate_hour_labels(start: datetime, hours: int = 24) -> List[str]:
    """Gibt ISO-Stundenlabels (UTC) zurück – pure Funktion."""
    start = start.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    return [(start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00") for i in range(hours)]

def generate_grid(center_lat: float, center_lon: float, radius_m: float, step_m: float) -> List[Tuple[float, float]]:
    """
    Erzeugt um (lat, lon) ein einfaches Raster (nur Koordinaten, keine I/O).
    Implementierung hier exemplarisch; nimm deine bestehende Logik falls vorhanden.
    """
    # Platzhalter: ersetze durch deine bewährte Variante
    return [(center_lat, center_lon)]

def map_forecast_to_grid(hourly_precip: List[float], grid: Iterable[Tuple[float, float]]) -> List[Tuple[float, float, List[float]]]:
    """
    Ordnet allen Gridpunkten die gleichen 24h-Werte zu (falls API nur einen Punkt liefert).
    Pure Funktion – kein Schreiben/Lesen.
    """
    return [(lat, lon, list(hourly_precip)) for (lat, lon) in grid]
