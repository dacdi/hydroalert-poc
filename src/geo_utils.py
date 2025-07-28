# src/geo_utils.py

from geopy.distance import distance
from geopy.point import Point
from typing import List, Tuple


def generate_grid(center_lat: float, center_lon: float, radius_km: int = 10, step_km: int = 2) -> List[Tuple[float, float]]:
    """
    Erzeugt ein 2D-Gitter von Koordinatenpunkten um einen Mittelpunkt.

    Args:
        center_lat (float): Breitengrad des Mittelpunkts.
        center_lon (float): Längengrad des Mittelpunkts.
        radius_km (int): Radius um den Mittelpunkt in Kilometern (in jede Richtung).
        step_km (int): Schrittweite zwischen den Punkten in Kilometern.

    Returns:
        List[Tuple[float, float]]: Liste von (lat, lon)-Tupeln.
    """
    center = Point(center_lat, center_lon)
    coords = []

    for dy in range(-radius_km, radius_km + 1, step_km):
        for dx in range(-radius_km, radius_km + 1, step_km):
            north_point = distance(kilometers=dy).destination(center, bearing=0)
            east_point = distance(kilometers=dx).destination(north_point, bearing=90)
            coords.append((east_point.latitude, east_point.longitude))

    return coords
