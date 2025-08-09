# src/services/forecast_area.py
from typing import List, Tuple
from datetime import datetime, timezone
from src.io.forecast_client import fetch_forecast_24h
from src.analysis.grid_ops import generate_hour_labels, generate_grid, map_forecast_to_grid
from src.io.file_io import ensure_dir
from src.utils.utils_logger import get_logger
from src.config.config import RAIN_GRID_PATH
import csv
import os

logger = get_logger()

def save_forecast_grid_to_cache(lat: float, lon: float, radius_m: float = 2000.0, step_m: float = 200.0) -> str:
    """
    Holt 24h-Vorhersage, baut ein Raster, projiziert Werte und speichert als CSV.
    """
    logger.info("📡 Fetch forecast for lat=%.4f lon=%.4f", lat, lon)
    raw = fetch_forecast_24h(lat, lon)

    # 1) Werte extrahieren (passe die Keys an dein API-Schema an)
    hourly = raw.get("hourly", {})
    precip = hourly.get("precipitation", [])
    if not precip:
        logger.warning("⚠️ No precipitation data in API response")
        precip = [0.0] * 24

    # 2) Grid & Labels (pure analysis)
    start = datetime.now(timezone.utc)
    labels = generate_hour_labels(start, hours=min(24, len(precip)))
    grid = generate_grid(lat, lon, radius_m=radius_m, step_m=step_m)
    grid_with_values = map_forecast_to_grid(precip[:len(labels)], grid)

    # 3) CSV schreiben (I/O hier im Service)
    outpath = os.path.abspath(RAIN_GRID_PATH)
    ensure_dir(os.path.dirname(outpath))
    _write_grid_csv(outpath, labels, grid_with_values)
    logger.info("✅ Saved forecast grid: %s", outpath)
    return outpath

def _write_grid_csv(path: str, hour_labels: List[str], rows: List[Tuple[float, float, List[float]]]) -> None:
    header = ["lat", "lon"] + hour_labels
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for lat, lon, vals in rows:
            writer.writerow([f"{lat:.5f}", f"{lon:.5f}", *[f"{v:.2f}" for v in vals]])
