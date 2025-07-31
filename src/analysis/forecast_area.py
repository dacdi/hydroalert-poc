# src/forecast_area.py

from typing import List
from time import sleep
from datetime import datetime, timedelta
import os
import csv
import pytz
import logging

from src.utils.geo_utils import generate_grid
from src.io.fetch_weather import fetch_forecast_data

logger = logging.getLogger(__name__)


def get_hour_labels(start: datetime, hours: int = 24) -> List[str]:
    """
    Gibt eine Liste formatierter Zeitstempel für die nächsten `hours` Stunden zurück.
    """
    return [
        (start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00")
        for i in range(hours)
    ]


def save_full_rain_forecast_grid(
    output_path: str = "output/rain_grid_24h.csv",
    center_lat: float = 49.35,
    center_lon: float = 8.15,
    radius_km: int = 10,
    step_km: int = 5,
    delay: float = 0.2,
) -> None:
    """
    Holt für jeden Rasterpunkt die nächsten 24 Stunden Regenvorhersage
    und speichert sie in einer CSV-Datei mit einem Eintrag pro Rasterpunkt.

    Args:
        output_path: Pfad zur Ausgabedatei
        center_lat: Mittelpunkt des Rasters (Breitengrad)
        center_lon: Mittelpunkt des Rasters (Längengrad)
        radius_km: Radius um den Mittelpunkt
        step_km: Abstand zwischen Rasterpunkten in km
        delay: Pausenzeit zwischen API-Anfragen in Sekunden
    """
    logger.info(
        f"🌍 Starte Flächen-Rastergenerierung: Zentrum=({center_lat}, {center_lon}), "
        f"Radius={radius_km} km, Schritt={step_km} km"
    )
    grid = generate_grid(center_lat, center_lon, radius_km, step_km)
    total_points = len(grid)
    logger.info(f"📏 Rastergröße: {total_points} Punkte")

    now = datetime.now(pytz.timezone("Europe/Berlin"))
    hour_labels = get_hour_labels(now, 24)
    logger.debug(f"🕒 Stundenziele: {hour_labels}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["Breitengrad", "Längengrad"] + [f"Regen_{i}h" for i in range(24)]
        writer.writerow(header)

        for idx, (lat, lon) in enumerate(grid, start=1):
            logger.debug(f"📍 Punkt {idx}/{total_points}: ({lat:.5f}, {lon:.5f})")
            data = fetch_forecast_data(lat, lon)

            if data is None:
                logger.warning(f"⚠️ Keine Vorhersagedaten für ({lat}, {lon}) – leere Werte eingetragen")
                rain_series = [None] * 24
            else:
                rain_series = []
                for label in hour_labels:
                    try:
                        idx_time = data["hourly"]["time"].index(label)
                        rain = data["hourly"]["precipitation"][idx_time]
                    except (ValueError, KeyError, TypeError):
                        logger.debug(f"⏳ Kein Regenwert für Stunde {label} an ({lat}, {lon})")
                        rain = None
                    rain_series.append(rain)

            writer.writerow([f"{lat:.5f}", f"{lon:.5f}"] + rain_series)

            if idx % 10 == 0 or idx == total_points:
                logger.info(f"✅ Fortschritt: {idx}/{total_points} Rasterpunkte verarbeitet")

            sleep(delay)

    logger.info(f"📁 CSV gespeichert unter: {output_path}")
