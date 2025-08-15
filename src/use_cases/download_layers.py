# src/use_cases/download_layers.py

from argparse import Namespace
from logging import Logger

from src.services.wms_downloader_service import (
    download_layers_for_latlon,
    download_layers_default,
)
from src.utils.utils_logger import get_logger
from src.utils.naming import cache_path_for_latlon

logger: Logger = get_logger()


def run_download_layers_use_case(args: Namespace) -> None:
    """
    Orchestriert den WMS-Download:
      - mit lat/lon: Service übernimmt BBox-Bildung intern (Analysis) und speichert in den Geo-Cache-Ordner
      - ohne lat/lon: Service lädt per DEFAULT_BBOX in den Standardordner
    """
    logger.info("🌐 Lade WMS-Layer …")

    lat = getattr(args, "lat", None)
    lon = getattr(args, "lon", None)

    if lat is not None and lon is not None:
        lat = float(lat)
        lon = float(lon)
        target_dir = cache_path_for_latlon(lat, lon)
        logger.debug("Zielordner (Geo-Cache): %s", target_dir)
        download_layers_for_latlon(lat=lat, lon=lon, target_dir=target_dir)
    else:
        download_layers_default()

    logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")
