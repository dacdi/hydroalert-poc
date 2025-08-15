# src/services/telegram_bot_service.py

import os
from glob import glob
from typing import Optional, List
from pyproj import Transformer

from src.domain.models import BBox
from src.services.wms_downloader_service import download_all_wms_layers
from src.services.cache_generation_service import generate_cache_for_location
from src.config.config import OSM_RADIUS_M, SAMPLE_DISTANCE_M, DEFAULT_LAYERS
from src.utils.naming import cache_path_for_latlon
from src.utils.utils_logger import get_logger

logger = get_logger()

# WGS84 -> EPSG:25832 (ETRS89 / UTM32)
_TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)


def _latlon_to_xy25832(lon: float, lat: float) -> tuple[float, float]:
    x, y = _TRANSFORMER.transform(lon, lat)
    return x, y


def _bbox_from_latlon(lat: float, lon: float, radius_m: int) -> BBox:
    x, y = _latlon_to_xy25832(lon, lat)
    return BBox(int(x - radius_m), int(y - radius_m), int(x + radius_m), int(y + radius_m))


def _wms_inputs_present(cache_dir: str, required_layers: Optional[List[str]] = None) -> bool:
    """
    Prüft, ob meta.json und die PNGs der (relevanten) Layer im Geo-Cache-Verzeichnis liegen.
    """
    meta_ok = os.path.isfile(os.path.join(cache_dir, "meta.json"))
    layers = required_layers or list(DEFAULT_LAYERS.values())
    png_ok = all(os.path.isfile(os.path.join(cache_dir, f"{short}.png")) for short in layers)
    logger.debug("WMS-Inputs present? meta=%s, pngs=%s in %s", meta_ok, png_ok, cache_dir)
    return meta_ok and png_ok


def _find_any_kml(cache_dir: str) -> Optional[str]:
    """
    Liefert eine sinnvolle KML-Datei aus dem Cache, falls vorhanden.
    Bevorzugt SRI10_1h, dann SRI7_1h, dann SRI10_4h; sonst erste gefundene.
    """
    preferred = ["Wassertiefe_SRI10_1h", "Wassertiefe_SRI7_1h", "Wassertiefe_SRI10_4h"]
    for short in preferred:
        path = os.path.join(cache_dir, f"flood_{short}.kml")
        if os.path.isfile(path):
            return path
    matches = sorted(glob(os.path.join(cache_dir, "flood_*.kml")))
    return matches[0] if matches else None


def handle_message_logic(lat: float, lon: float):
    """
    Minimal-Workflow für Telegram:
    - Prüfen, ob KML bereits im Cache liegt → sofort zurück
    - Sonst WMS-Layer für die Koordinaten in den Geo-Cache laden
    - Danach Cache generieren (CSV/KML)
    - Falls möglich, eine KML zurückgeben
    """
    logger.info("📩 Anfrage für Koordinaten: %.6f, %.6f", lat, lon)
    cache_dir = cache_path_for_latlon(lat, lon)
    os.makedirs(cache_dir, exist_ok=True)
    logger.debug("🗂️ Cache-Verzeichnis: %s", cache_dir)

    # 1) Bereits fertige KML vorhanden?
    kml_path = _find_any_kml(cache_dir)
    if kml_path:
        logger.info("✅ KML bereits vorhanden: %s", os.path.relpath(kml_path))
        return "📦 Daten aus Cache gefunden.", kml_path

    # 2) WMS-Inputs vorhanden? Wenn nicht, jetzt herunterladen
    if not _wms_inputs_present(cache_dir):
        bbox = _bbox_from_latlon(lat, lon, int(OSM_RADIUS_M))
        logger.info("⬇️ WMS-Inputs fehlen → Download starte (BBox=%s, Ziel=%s)", bbox, cache_dir)
        try:
            download_all_wms_layers(bbox=bbox, target_dir=cache_dir)
        except Exception:
            logger.exception("Fehler beim WMS-Download")
            return "❌ Fehler beim Herunterladen der Karten-Layer.", None

    # 3) Cache generieren (Straßentiefe berechnen & KML/CSV schreiben)
    logger.info("🔧 Starte Cache-Generierung …")
    try:
        status = generate_cache_for_location(
            lat=lat,
            lon=lon,
            radius_m=OSM_RADIUS_M,
            sample_distance_m=SAMPLE_DISTANCE_M,
            layers=list(DEFAULT_LAYERS.values()),
        )
        logger.debug("Generate-Status: %s", status)
    except Exception:
        logger.exception("Fehler bei der Cache-Generierung")
        return "❌ Fehler bei der Analyse/Cache-Erzeugung.", None

    # 4) Nach der Generierung erneut nach KML schauen
    kml_path = _find_any_kml(cache_dir)
    if kml_path:
        logger.info("✅ KML erzeugt: %s", os.path.relpath(kml_path))
        return "✅ Daten erstellt und im Cache gespeichert.", kml_path

    logger.warning("⚠️ Generierung abgeschlossen, aber keine KML gefunden.")
    return "✅ Daten erstellt, aber keine KML-Datei gefunden.", None


def run_bot():
    """Startet den Telegram-Bot (ruft IO-Adapter auf)."""
    from src.io.telegram_adapter import start_bot
    start_bot(handle_message_logic)
