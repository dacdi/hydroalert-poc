from argparse import Namespace
from logging import Logger
from typing import Tuple, Optional
from pyproj import Transformer

from src.services.wms_downloader import download_all_wms_layers
from src.utils.utils_logger import get_logger
from src.io.wms_client import BBox
from src.utils.naming import cache_path_for_latlon

logger: Logger = get_logger()

_TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)

def _latlon_to_xy25832(lon: float, lat: float) -> Tuple[float, float]:
    x, y = _TRANSFORMER.transform(lon, lat)
    return x, y

def _bbox_from_latlon(lat: float, lon: float, radius_m: int = 2000) -> BBox:
    x, y = _latlon_to_xy25832(lon, lat)
    return BBox(int(x - radius_m), int(y - radius_m), int(x + radius_m), int(y + radius_m))

def run_download_layers_use_case(args: Namespace) -> None:
    """
    Speichert WMS-Layer in data/cache/lat{:.2f}_lon{:.2f}/, wenn --lat/--lon übergeben sind.
    Ohne lat/lon: Standardziel aus config (WMS_LAYERS_DIR).
    """
    logger.info("🌐 Lade WMS-Layer …")

    lat = getattr(args, "lat", None)
    lon = getattr(args, "lon", None)

    if lat is not None and lon is not None:
        lat = float(lat); lon = float(lon)
        bbox = _bbox_from_latlon(lat, lon)
        target_dir = cache_path_for_latlon(lat, lon)
        logger.debug("🧭 lat/lon -> BBox=%s; Zielordner=%s", bbox, target_dir)
        download_all_wms_layers(bbox=bbox, target_dir=target_dir)
    else:
        # Fallback: alles per Defaults (keine lat/lon → kein spezieller Cache-Ordner)
        download_all_wms_layers()

    logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")
