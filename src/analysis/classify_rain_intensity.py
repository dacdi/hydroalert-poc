import csv
import os
from typing import List, Tuple

from src.utils.utils_logger import get_logger
from src.config.config import RAIN_GRID_PATH

# Schwellenwerte
SRI7_THRESHOLD = 15            # mm/h
SRI10_THRESHOLD = 25           # mm/h
SRI10_4H_SUM_THRESHOLD = 40    # mm in 4h (Summe)
MIN_AREA_FRACTION = 0.5        # 50 %

logger = get_logger()


def read_rain_rows(csv_path: str) -> List[List[float]]:
    """Load all valid rain value rows from a CSV file."""
    if not os.path.exists(csv_path):
        logger.error(f"❌ Datei nicht gefunden: {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        try:
            next(reader)
        except StopIteration:
            logger.error("❌ CSV-Datei ist leer.")
            raise ValueError("CSV file is empty.")

        rows: List[List[float]] = []
        for row in reader:
            try:
                values = [float(v) for v in row[2:] if v]
                if len(values) >= 4:
                    rows.append(values)
            except ValueError:
                continue
    return rows


def count_threshold_exceedances(rain_rows: List[List[float]]) -> Tuple[int, int, int, int]:
    """Count how many raster cells exceed each threshold."""
    total = len(rain_rows)
    count_sri10 = 0
    count_sri10_4h = 0
    count_sri7 = 0
    for rain_values in rain_rows:
        max_1h = max(rain_values)
        max_4h_sum = max(
            sum(rain_values[i:i + 4]) for i in range(len(rain_values) - 3)
        )
        if max_1h >= SRI10_THRESHOLD:
            count_sri10 += 1
        if max_4h_sum >= SRI10_4H_SUM_THRESHOLD:
            count_sri10_4h += 1
        if max_1h >= SRI7_THRESHOLD:
            count_sri7 += 1
    return total, count_sri10, count_sri10_4h, count_sri7


def log_threshold_stats(total: int, count_sri10: int, count_sri10_4h: int, count_sri7: int) -> None:
    """Log the ratio of raster cells exceeding each threshold."""
    logger.info(
        f"🌧️ Analyse abgeschlossen: "
        f"{count_sri10}/{total} Raster mit SRI10_1h, "
        f"{count_sri10_4h}/{total} mit SRI10_4h, "
        f"{count_sri7}/{total} mit SRI7"
    )


def decide_layer(total: int, count_sri10: int, count_sri10_4h: int, count_sri7: int) -> str:
    """Return the layer name based on exceedance ratios."""
    if count_sri10 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI10_1h"
    if count_sri10_4h / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI10_4h"
    if count_sri7 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI7_1h"
    return "Schummerung"


def classify_rain_stage(csv_path: str = RAIN_GRID_PATH) -> str:
    """Analyse rain raster data and return the matching layer name."""
    rain_rows = read_rain_rows(csv_path)
    if not rain_rows:
        logger.error("❌ Keine gültigen Regenwerte gefunden.")
        raise ValueError("No valid rainfall data found in CSV.")

    total, count_sri10, count_sri10_4h, count_sri7 = count_threshold_exceedances(rain_rows)
    log_threshold_stats(total, count_sri10, count_sri10_4h, count_sri7)
    return decide_layer(total, count_sri10, count_sri10_4h, count_sri7)
