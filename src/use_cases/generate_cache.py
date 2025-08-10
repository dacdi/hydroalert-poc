from argparse import Namespace
from logging import Logger

from src.io.flood_cache import generate_csv_cache
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


def run_generate_cache_use_case(args: Namespace) -> None:
    """Generate CSV and KML caches for flood data."""
    logger.info("🗄 Generiere Flood-CSV-Cache …")
    generate_csv_cache(
        radius_m=args.radius,
        sample_distance_m=args.sample_distance,
    )
    logger.info("✅ Cache-Erzeugung abgeschlossen.")
