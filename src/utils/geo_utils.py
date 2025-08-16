# src/utils/geo_utils.py
from __future__ import annotations

from math import cos, radians
from typing import List, Tuple


def generate_grid(
    center_lat: float,
    center_lon: float,
    *,
    half_extent_km: float,
    step_km: float,
) -> List[Tuple[float, float]]:
    """
    Erzeugt ein **quadratisches** Raster um (center_lat, center_lon) in WGS84.

    Parameter:
        half_extent_km: Halbe Kantenlänge des Quadrats in Kilometern
                        (z. B. 0.2 → Quadrat ist 0.4 km × 0.4 km)
        step_km:        Rasterabstand in Kilometern zwischen benachbarten Punkten

    Rückgabe:
        Liste von (lat, lon)-Tupeln.

    Hinweise:
    - Umrechnung km→Grad erfolgt lokal am Mittelpunkt:
        1° Breite  ≈ 111.32 km
        1° Länge   ≈ 111.32 * cos(lat) km
    - Für kleine Bereiche (einige km) ist diese Approximation ausreichend genau.
    - Kein I/O, keine externen Abhängigkeiten.
    """
    if half_extent_km <= 0 or step_km <= 0:
        return [(center_lat, center_lon)]

    KM_PER_DEG_LAT = 111.32
    km_per_deg_lon = 111.32 * max(1e-12, cos(radians(center_lat)))  # Schutz vor Polnähe

    lat_step_deg = step_km / KM_PER_DEG_LAT
    lon_step_deg = step_km / km_per_deg_lon
    lat_half_deg = half_extent_km / KM_PER_DEG_LAT
    lon_half_deg = half_extent_km / km_per_deg_lon

    def frange(start: float, stop: float, step: float):
        """Float-Schrittweite inkl. numerischer Toleranz (inklusiv stop)."""
        if step <= 0:
            return
        x = start
        eps = abs(step) * 1e-9
        while x <= stop + eps:
            yield x
            x += step

    points: List[Tuple[float, float]] = []
    for dlat in frange(-lat_half_deg, lat_half_deg, lat_step_deg):
        lat = center_lat + dlat
        for dlon in frange(-lon_half_deg, lon_half_deg, lon_step_deg):
            lon = center_lon + dlon
            points.append((lat, lon))

    return points or [(center_lat, center_lon)]
