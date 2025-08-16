# src/analysis/geo_transforms.py

from typing import Tuple
from pyproj import Transformer
from src.domain.models import BBox
from src.utils.utils_logger import get_logger

logger = get_logger()

# WGS84 -> EPSG:25832 (ETRS89 / UTM32); always_xy=True: (lon, lat) Reihenfolge
_TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)


def latlon_to_xy25832(lon: float, lat: float) -> Tuple[float, float]:
    """Transformiert (lon, lat) in EPSG:25832 (x, y)."""
    logger.debug("geo_transforms.latlon_to_xy25832(start): lon=%.6f, lat=%.6f", lon, lat)
    x, y = _TRANSFORMER.transform(lon, lat)
    logger.debug("geo_transforms.latlon_to_xy25832(result): x=%.3f, y=%.3f", x, y)
    return x, y


def bbox_from_latlon(lat: float, lon: float, radius_m: int = 2000) -> BBox:
    """
    Bildet eine quadratische BBox mit Kantenhalbweite radius_m (Meter)
    um die Position (lat, lon) in EPSG:25832.
    """
    x, y = latlon_to_xy25832(lon, lat)
    bbox = BBox(int(x - radius_m), int(y - radius_m), int(x + radius_m), int(y + radius_m))
    logger.debug("geo_transforms.bbox_from_latlon: %s", bbox)
    return bbox
