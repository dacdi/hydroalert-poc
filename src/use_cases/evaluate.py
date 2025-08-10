from argparse import Namespace
from logging import Logger

from src.analysis.classify_rain_intensity import classify_rain_stage
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


def run_evaluate_use_case(args: Namespace) -> None:
    """Classify rain intensity based on existing forecast data."""
    logger.info("🌍 Starte mit Analyse vorhandener Regendaten")
    result = classify_rain_stage()
    logger.info(f"✅ Empfohlener Layer: {result}")
