# src/use_cases/generate_cache.py
import argparse
from src.services.cache_generation_service import generate_cache_for_location
from src.utils.utils_logger import get_logger
from src.config.config import OSM_RADIUS_M, SAMPLE_DISTANCE_M

logger = get_logger()

def run_generate_cache_use_case(args: argparse.Namespace) -> None:
    lat = getattr(args, "lat", None)
    lon = getattr(args, "lon", None)
    radius_m = float(getattr(args, "radius_m", 1000.0))
    sample_m = float(getattr(args, "sample_m", 2.5))
    layers = getattr(args, "layers", None)  # optional, Liste aus main.py

    if lat is None or lon is None:
        logger.error("❌ --lat und --lon sind erforderlich.")
        raise ValueError("Fehlende Koordinaten.")

    status = generate_cache_for_location(
        lat=float(lat),
        lon=float(lon),
        radius_m=OSM_RADIUS_M,
        sample_distance_m=SAMPLE_DISTANCE_M,
        layers=layers,
    )
    logger.info("Ergebnis: %s", status)
