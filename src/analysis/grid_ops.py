# src/analysis/grid_ops.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

from src.utils.utils_logger import get_logger
from src.utils.geo_utils import generate_grid as _generate_grid_km  # expects half_extent_km, step_km

logger = get_logger()


def generate_hour_labels(start_utc: datetime, hours: int = 24) -> List[str]:
    """
    Erzeugt Stunden-Labels in UTC im Format YYYY-MM-DDTHH:00.
    IO-frei, reine Formatierung.
    """
    base = start_utc.replace(minute=0, second=0, microsecond=0)
    labels = [(base + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00") for i in range(hours)]
    logger.debug(
        "generate_hour_labels: %d Labels ab %s",
        len(labels),
        labels[0] if labels else "—",
    )
    return labels


def generate_grid(
    center_lat: float,
    center_lon: float,
    *,
    half_extent_km: float,
    step_m: float,
) -> List[Tuple[float, float]]:
    """
    Forecast-spezifischer Wrapper für die generische Rasterfunktion.
    Nimmt Meter entgegen, wandelt in Kilometer und delegiert an utils.geo_utils.generate_grid.
    Erwartet dort ein quadratisches Raster (kein I/O).
    """
    if half_extent_km <= 0 or step_m <= 0:
        logger.warning(
            "generate_grid: ungültige Parameter (half_extent_km=%.3f, step_m=%.3f) – gebe nur Mittelpunkt zurück.",
            half_extent_km,
            step_m,
        )
        return [(center_lat, center_lon)]

    half_extent_km = float(half_extent_km) / 1000.0
    step_km = float(step_m) / 1000.0

    points = _generate_grid_km(
        center_lat=center_lat,
        center_lon=center_lon,
        half_extent_km=half_extent_km,
        step_km=step_km,
    )
    logger.debug(
        "generate_grid: %d Punkte für center=(%.6f, %.6f), r=%.1fm, s=%.1fm",
        len(points),
        center_lat,
        center_lon,
        half_extent_km,
        step_m,
    )
    return points
