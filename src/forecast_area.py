from typing import Tuple, List
from time import sleep
from datetime import datetime
import os
import csv

from src.geo_utils import generate_grid
from src.fetch_weather import get_rain_forecast


def get_rain_area(
    min_rain_threshold: float = 5.0,
    delay: float = 0.2,
    center_lat: float = 49.35,
    center_lon: float = 8.15,
    radius_km: int = 10,
    step_km: int = 5
) -> Tuple[float, int, int, List[Tuple[float, float]], List[float | None]]:
    """
    Berechnet die überflutete Fläche um einen Mittelpunkt basierend auf einem Schwellenwert.

    Returns:
        Tuple:
            - betroffene Fläche in km²
            - Anzahl über Schwelle
            - Gesamtanzahl Punkte
            - Liste Koordinaten (Raster)
            - Liste Regenwerte
    """
    grid = generate_grid(center_lat, center_lon, radius_km, step_km)
    matched_points = 0
    rain_values = []

    for lat, lon in grid:
        rain = get_rain_forecast(lat, lon)
        rain_values.append(rain)

        if rain is not None and rain >= min_rain_threshold:
            matched_points += 1

        sleep(delay)

    total_points = len(grid)
    cell_area_km2 = step_km * step_km
    total_area_km2 = matched_points * cell_area_km2

    return total_area_km2, matched_points, total_points, grid, rain_values


def save_rain_grid(
    grid: List[Tuple[float, float]],
    rain_values: List[float | None],
    threshold: float,
    output_path: str
) -> None:
    """
    Speichert alle Rasterpunkte mit Regenwerten und Schwellenprüfung in eine CSV-Datei.

    Args:
        grid: Liste der (lat, lon) Koordinaten
        rain_values: Liste der zugehörigen Regenwerte (mm/h)
        threshold: Schwellenwert für Starkregen
        output_path: Speicherort für CSV
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    timestamp = datetime.now().isoformat()

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Breitengrad", "Längengrad", "Regen (mm/h)", "Überschwellig", "Zeitstempel"])

        for (lat, lon), rain in zip(grid, rain_values):
            if rain is None:
                writer.writerow([lat, lon, "", "", timestamp])
            else:
                is_over = rain >= threshold
                writer.writerow([lat, lon, f"{rain:.1f}", is_over, timestamp])
