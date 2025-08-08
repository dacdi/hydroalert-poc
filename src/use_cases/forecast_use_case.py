from argparse import Namespace
from logging import Logger
import os
import sys

from src.analysis.forecast_area import RainGridForecaster
from src.config.config import CACHE_DIR
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


def save_forecast_grid_to_cache(lat: float, lon: float) -> None:
    """Save the 24h forecast grid for the location to the cache directory."""
    raise NotImplementedError


def save_street_depths_to_cache(lat: float, lon: float) -> None:
    """Save detected street depths for the location to the cache directory."""
    raise NotImplementedError


def build_kml_for_location(lat: float, lon: float) -> None:
    """Build a KML overlay for the location and store it in the cache."""
    raise NotImplementedError


def run_forecast_use_case(args: Namespace) -> None:
    """Generate a rain forecast grid for given coordinates."""
    if args.lat is None or args.lon is None:
        logger.error(
            "❌ Bitte gib sowohl --lat als auch --lon an, z. B. --lat 49.45 --lon 8.18"
        )
        sys.exit(1)

    lat = round(args.lat, 4)
    lon = round(args.lon, 4)
    logger.info(f"📍 Vorhersage für Koordinaten: lat={lat}, lon={lon}")

    forecaster = RainGridForecaster(center_lat=lat, center_lon=lon)
    forecaster.save_full_rain_forecast_grid()
    logger.info("✅ Vorhersage erfolgreich gespeichert.")


def prepare_location_if_needed(lat: float, lon: float) -> None:
    """Ensure forecast and KML data for the location exist in the cache."""
    cache_dir = os.path.join(CACHE_DIR, f"lat{lat}_lon{lon}")
    forecast_path = os.path.join(cache_dir, "forecast_24h.csv")
    kml_path = os.path.join(cache_dir, "flutkarte.kml")

    if os.path.isfile(forecast_path) and os.path.isfile(kml_path):
        logger.info("✅ Daten bereits vorhanden")
        return

    logger.info("🔄 Erzeuge neue Standortdaten …")
    os.makedirs(cache_dir, exist_ok=True)
    save_forecast_grid_to_cache(lat, lon)
    save_street_depths_to_cache(lat, lon)
    build_kml_for_location(lat, lon)
