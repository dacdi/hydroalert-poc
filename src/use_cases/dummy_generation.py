from argparse import Namespace
from logging import Logger

from src.io.generate_dummy_data import generate_dummy_rain_data
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


def run_dummy_generation_use_case(args: Namespace) -> None:
    """Generate dummy rain data for testing."""
    logger.info("🧪 Generating dummy rain data …")
    logger.debug(f"Using variant for rain intensity: {args.variant}")
    generate_dummy_rain_data(variant=args.variant)
