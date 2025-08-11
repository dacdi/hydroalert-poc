# src/services/dummy_data_service.py
import os
from typing import Optional, Dict
from datetime import datetime, timezone

from src.analysis.dummy_rain import make_dummy_series
from src.config.config import RAIN_THRESHOLDS
from src.io.rain_csv_store import save_rain_grid_csv
from src.utils.naming import cache_path_for_latlon, rain_grid_csv_name
from src.utils.utils_logger import get_logger

logger = get_logger()


def generate_dummy_for_location(
    lat: float,
    lon: float,
    variant: str,
    csv_path_override: Optional[str] = None,
    hours: int = 24,
    start_utc: Optional[datetime] = None,
    thresholds: Optional[Dict[str, float]] = None,
) -> str:
    """
    Erzeugt eine Dummy-Regen-CSV für einen Ort und speichert sie im Geo-Cache-Ordner.
    """
    th = thresholds or RAIN_THRESHOLDS
    logger.debug(
        "generate_dummy_for_location(start): lat=%s lon=%s variant=%s hours=%s",
        lat, lon, variant, hours
    )

    series = make_dummy_series(variant=variant, thresholds=th, hours=hours)

    cache_dir = cache_path_for_latlon(lat, lon)
    csv_path = csv_path_override or os.path.join(cache_dir, rain_grid_csv_name(lat, lon))
    csv_path = os.path.abspath(csv_path)

    save_rain_grid_csv(
        path=csv_path,
        lat=lat,
        lon=lon,
        hourly_values=series,
        start_utc=start_utc or datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0),
    )
    logger.info(f"✅ Dummy '{variant}' erzeugt: {csv_path}")
    return csv_path
