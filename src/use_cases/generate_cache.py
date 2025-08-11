# src/use_cases/generate_cache.py
import argparse
from src.services.cache_generation_service import generate_cache_for_location
from src.utils.utils_logger import get_logger

logger = get_logger()

def run_generate_cache_use_case(args: argparse.Namespace) -> None:
    lat = getattr(args, "lat", None)
    lon = getattr(args, "lon", None)
    radius_m = float(getattr(args, "radius_m", 300.0))
    sample_m = float(getattr(args, "sample_m", 5.0))
    layers = getattr(args, "layers", None)  # optional, Liste aus main.py

    if lat is None or lon is None:
        logger.error("❌ --lat und --lon sind erforderlich.")
        raise ValueError("Fehlende Koordinaten.")

    status = generate_cache_for_location(
        lat=float(lat),
        lon=float(lon),
        radius_m=radius_m,
        sample_distance_m=sample_m,
        layers=layers,
    )
    logger.info("Ergebnis: %s", status)
