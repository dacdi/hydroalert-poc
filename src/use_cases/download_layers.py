# src/use_cases/download_layers.py

from argparse import Namespace
from logging import Logger

from src.services.wms_downloader_service import download_all_wms_layers
from src.analysis.geo_transforms import bbox_from_latlon
from src.utils.utils_logger import get_logger
from src.utils.naming import cache_path_for_latlon

logger: Logger = get_logger()


def run_download_layers_use_case(args: Namespace) -> None:
    """
    Wenn --lat/--lon gesetzt:
      - bilde BBox (2000 m Halbbreite) via analysis.geo_transforms
      - speichere alle WMS-Layer unter data/cache/latXX.XX_lonYY.YY/
    sonst:
      - nutze reine Defaults aus config (Standard-BBox und -Zielordner)
    """
    logger.info("🌐 Lade WMS-Layer …")

    lat = getattr(args, "lat", None)
    lon = getattr(args, "lon", None)

    if lat is not None and lon is not None:
        lat = float(lat)
        lon = float(lon)
        bbox = bbox_from_latlon(lat, lon)  # aus analysis
        target_dir = cache_path_for_latlon(lat, lon)
        logger.debug("🧭 lat/lon -> BBox=%s; Zielordner=%s", bbox, target_dir)
        download_all_wms_layers(bbox=bbox, target_dir=target_dir)
    else:
        download_all_wms_layers()

    logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")
