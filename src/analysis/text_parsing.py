# src/analysis/text_parsing.py
from __future__ import annotations
import re
from typing import Optional, Tuple

from src.utils.utils_logger import get_logger

logger = get_logger()

_COORD_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)")


def parse_lat_lon(text: str) -> Optional[Tuple[float, float]]:
    """Extrahiert Dezimalgrad (lat, lon) aus freiem Text. Pure, ohne I/O."""
    logger.debug("parse_lat_lon input=%r", text)
    m = _COORD_RE.search(text)
    if not m:
        logger.debug("parse_lat_lon no match")
        return None
    lat, lon = float(m.group(1)), float(m.group(2))
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        logger.debug("parse_lat_lon out of bounds lat=%s lon=%s", lat, lon)
        return None
    logger.debug("parse_lat_lon parsed lat=%.6f lon=%.6f", lat, lon)
    return lat, lon
