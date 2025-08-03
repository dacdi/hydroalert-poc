import csv
import os
from typing import List

from src.utils.utils_logger import get_logger
from src.config.config import RAIN_GRID_PATH

# Schwellenwerte
SRI7_THRESHOLD = 15            # mm/h
SRI10_THRESHOLD = 25           # mm/h
SRI10_4H_SUM_THRESHOLD = 40    # mm in 4h (Summe)
MIN_AREA_FRACTION = 0.5        # 50 %

logger = get_logger()


def classify_rain_stage(csv_path: str = RAIN_GRID_PATH) -> str:
    """
    Analysiert ein CSV mit 24h-Regenraster und gibt den passenden Layernamen zurück.

    Args:
        csv_path (str): Pfad zur CSV-Datei mit Niederschlagsdaten (mm/h pro Stunde).

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
    total = 0
    count_sri10 = 0
    count_sri10_4h = 0
    count_sri7 = 0

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)  # Kopfzeile überspringen
        except StopIteration:
            logger.error("❌ CSV-Datei ist leer.")
            raise ValueError("CSV file is empty.")

        for row in reader:
            try:
                rain_values = [float(v) for v in row[2:] if v]
                if not rain_values or len(rain_values) < 4:
                    continue

                total += 1
                max_1h = max(rain_values)
                max_4h_sum = max(
                    sum(rain_values[i:i+4]) for i in range(len(rain_values) - 3)
                )

                if max_1h >= SRI10_THRESHOLD:
                    count_sri10 += 1
                if max_4h_sum >= SRI10_4H_SUM_THRESHOLD:
                    count_sri10_4h += 1
                if max_1h >= SRI7_THRESHOLD:
                    count_sri7 += 1

            except ValueError:
                continue

    if total == 0:
        logger.error("❌ Keine gültigen Regenwerte gefunden.")
        raise ValueError("No valid rainfall data found in CSV.")

    # Logging der Anteile
    logger.info(
        f"🌧️ Analyse abgeschlossen: "
        f"{count_sri10}/{total} Raster mit SRI10_1h, "
        f"{count_sri10_4h}/{total} mit SRI10_4h, "
        f"{count_sri7}/{total} mit SRI7"
    )

    # Entscheidung nach Priorität
    if count_sri10 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI10_1h"
    elif count_sri10_4h / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI10_4h"
    elif count_sri7 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI7_1h"
    else:
        return "Schummerung"
