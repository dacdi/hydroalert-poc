import csv
import os
import logging
from typing import List

# Schwellenwerte in mm/h
SRI7_THRESHOLD = 15
SRI10_THRESHOLD = 25
MIN_AREA_FRACTION = 0.5  # 50 %

logger = logging.getLogger(__name__)

def classify_rain_stage(csv_path: str = "output/rain_grid_24h.csv") -> str:
    """
    Analysiert ein CSV mit 24h-Regenraster und gibt den passenden Layernamen zurück.

    Args:
        csv_path (str): Pfad zur CSV-Datei mit Niederschlagsdaten.

    Returns:
        str: Layername entsprechend der erkannten Starkregenstufe.

    Raises:
        FileNotFoundError: Wenn die Datei nicht existiert.
        ValueError: Wenn keine gültigen Regenwerte analysierbar sind.
    """
    if not os.path.exists(csv_path):
        logger.error(f"❌ Datei nicht gefunden: {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rain_max_values: List[float] = []

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)  # skip header
        except StopIteration:
            logger.error("❌ CSV-Datei ist leer.")
            raise ValueError("CSV file is empty.")

        for row in reader:
            try:
                rain_values = [float(v) for v in row[2:] if v]
                if rain_values:
                    max_rain = max(rain_values)
                    rain_max_values.append(max_rain)
            except ValueError:
                continue  # ignoriert ungültige Zeilen

    if not rain_max_values:
        logger.error("❌ Keine gültigen Regenwerte gefunden.")
        raise ValueError("No valid rainfall data found in CSV.")

    total = len(rain_max_values)
    count_sri10 = sum(1 for r in rain_max_values if r >= SRI10_THRESHOLD)
    count_sri7 = sum(1 for r in rain_max_values if r >= SRI7_THRESHOLD)

    if count_sri10 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI10_1h"
    elif count_sri7 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI7_1h"
    else:
        return "Schummerung"
