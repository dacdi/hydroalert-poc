# src/use_cases/generate_dummy.py
import argparse
from typing import Optional

from src.services.dummy_data_service import generate_dummy_for_location
from src.utils.utils_logger import get_logger

logger = get_logger()


def run_generate_dummy_use_case(args: argparse.Namespace) -> None:
    lat: Optional[float] = getattr(args, "lat", None)
    lon: Optional[float] = getattr(args, "lon", None)
    variant: str = getattr(args, "variant", "none")
    hours: int = int(getattr(args, "hours", 24))

    if lat is None or lon is None:
        logger.error("❌ Keine Koordinaten übergeben – bitte --lat und --lon angeben.")
        raise ValueError("Fehlende Koordinaten: --lat und --lon sind erforderlich.")

    path = generate_dummy_for_location(
        lat=lat,
        lon=lon,
        variant=variant,
        hours=hours,
    )
    logger.info(f"🗂️  Dummy-CSV erstellt: {path}")
