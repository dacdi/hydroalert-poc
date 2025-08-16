# src/services/cache_query_service.py

import os
from typing import Optional
from src.utils.naming import cache_path_for_latlon
from src.utils.utils_logger import get_logger

logger = get_logger()

def has_cached_result(lat: float, lon: float, layers: Optional[list[str]] = None) -> bool:
    """
    Prüft, ob für die angegebenen Koordinaten Cache-Daten vorhanden sind.
    Der Cache-Pfad basiert auf lat/lon, z.B.: data/cache/lat49.35_lon8.15/

    Args:
        lat: Breitengrad
        lon: Längengrad
        layers: Optionale Liste von Layer-Kurzbezeichnungen (z.B. ["Wassertiefe_SRI7_1h"])

    Returns:
        True, wenn alle erwarteten Dateien im Cache vorhanden sind, sonst False.
    """
    cache_dir = cache_path_for_latlon(lat, lon)
    logger.debug(f"Prüfe Cache-Pfad: {cache_dir}")

    if not os.path.isdir(cache_dir):
        logger.debug("Cache-Verzeichnis existiert nicht.")
        return False

    if not layers:
        files = os.listdir(cache_dir)
        logger.debug(f"Gefundene Dateien: {files}")
        return len(files) > 0

    for layer in layers:
        found = any(
            fname.startswith(layer) and (fname.endswith(".kml") or fname.endswith(".csv"))
            for fname in os.listdir(cache_dir)
        )
        if not found:
            logger.debug(f"Keine Cache-Datei gefunden für Layer: {layer}")
            return False

    logger.debug("Alle benötigten Cache-Dateien gefunden.")
    return True
