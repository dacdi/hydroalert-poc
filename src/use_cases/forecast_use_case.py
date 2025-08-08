from argparse import Namespace
from logging import Logger
import sys

from src.analysis.forecast_area import RainGridForecaster
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


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
