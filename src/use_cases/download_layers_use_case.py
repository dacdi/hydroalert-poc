from argparse import Namespace
from logging import Logger

from src.io.download_layers import download_all_wms_layers
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


def run_download_layers_use_case(args: Namespace) -> None:
    """Download all predefined WMS layers."""
    logger.info("🌐 Lade WMS-Layer herunter …")
    download_all_wms_layers()
    logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")
