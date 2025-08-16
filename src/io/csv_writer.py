# src/io/csv_writer.py
from __future__ import annotations
import csv
import os
from typing import List, Iterable, Tuple, Union

from src.utils.utils_logger import get_logger
from src.domain.rain_forecast import RainForecast

logger = get_logger()

RowType = Union[RainForecast, Tuple[float, float, list[float]]]

def write_rain_forecasts_csv(path: str, hour_labels: List[str], rows: Iterable[RowType]) -> str:
    """
    Schreibt CSV mit Header: latitude, longitude, <24x Labels>
    - latitude/longitude: 5 Nachkommastellen
    - Werte: auf 3 Nachkommastellen gerundet (mm/h)
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = ["latitude", "longitude"] + hour_labels

    count = 0
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for item in rows:
            if isinstance(item, RainForecast):
                lat, lon = item.point.lat, item.point.lon
                vals = item.hourly_values
            else:
                lat, lon, vals = item  # type: ignore[assignment]
            w.writerow([f"{lat:.5f}", f"{lon:.5f}", *[round(float(v), 3) for v in vals]])
            count += 1

    logger.info("📝 CSV geschrieben (%d Zeilen): %s", count, path)
    return os.path.abspath(path)
