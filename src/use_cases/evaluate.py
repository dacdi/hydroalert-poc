# src/use_cases/evaluate.py
import argparse
from typing import Optional

from src.services.evaluation_service import evaluate_and_store_for_location
from src.utils.utils_logger import get_logger

logger = get_logger()


def run_evaluate_use_case(args: argparse.Namespace) -> None:
    lat: Optional[float] = getattr(args, "lat", None)
    lon: Optional[float] = getattr(args, "lon", None)
    csv_override: Optional[str] = getattr(args, "csv", None)

    if lat is None or lon is None:
        logger.error("❌ Keine Koordinaten übergeben – bitte --lat und --lon angeben.")
        raise ValueError("Fehlende Koordinaten: --lat und --lon sind erforderlich.")

    rec = evaluate_and_store_for_location(
        lat=lat,
        lon=lon,
        csv_path_override=csv_override
    )
    logger.info("🗂️  evaluation.json im zugehörigen Geo-Cache-Ordner aktualisiert.")
