# src/services/wms_downloader_service.py

import os
import json
from typing import Optional, List
from PIL import Image

from src.domain.models import BBox
from src.analysis.geo_transforms import bbox_from_latlon
from src.io.wms_client import build_wms_params, fetch_wms_png
from src.io.file_io import ensure_dir, save_png
from src.config.config import (
    WMS_LAYERS_DIR,
    WMS_BASE_URL,
    DEFAULT_BBOX,
    DEFAULT_SIZE,
    DEFAULT_LAYERS,
    OSM_RADIUS_M,
)
from src.utils.utils_logger import get_logger

logger = get_logger()


def _save_meta_file(target_dir: str, bbox: BBox, png_path: str) -> None:
    """Speichert BBox und Rastergröße in meta.json."""
    width, height = Image.open(png_path).size
    meta = {
        "bbox_utm": [bbox.minx, bbox.miny, bbox.maxx, bbox.maxy],
        "raster_size": [width, height],
        "crs": "EPSG:25832",
    }
    meta_path = os.path.join(target_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    logger.info("💾 Meta-Datei gespeichert: %s", meta_path)


def download_all_wms_layers(*, bbox: BBox, target_dir: Optional[str] = None) -> List[str]:
    """
    Lädt alle vordefinierten WMS-Layer und speichert sie als PNG.
    Erwartet eine fertige BBox (EPSG:25832). Keine Default-BBox hier!
    """
    outdir = ensure_dir(target_dir or WMS_LAYERS_DIR)
    w, h = DEFAULT_SIZE

    saved: List[str] = []
    for full_layer, short_name in DEFAULT_LAYERS.items():
        logger.info("⬇️ Downloading layer: %s", full_layer)
        params = build_wms_params(full_layer, bbox, w, h)
        content = fetch_wms_png(WMS_BASE_URL, params)
        path = save_png(content, outdir, short_name)
        saved.append(path)

    if saved:
        _save_meta_file(outdir, bbox, saved[0])
    else:
        logger.warning("⚠️ Keine PNG-Dateien heruntergeladen – meta.json nicht erstellt.")

    logger.info("✅ %d Layer gespeichert in %s", len(saved), outdir)
    return saved


def download_layers_for_latlon(
    *, lat: float, lon: float, target_dir: Optional[str] = None, radius_m: int = int(OSM_RADIUS_M)
) -> List[str]:
    """
    Convenience: nimmt lat/lon entgegen, bildet intern die BBox (Analysis),
    und lädt dann alle WMS-Layer in target_dir (oder WMS_LAYERS_DIR).
    """
    bbox = bbox_from_latlon(lat, lon, radius_m=radius_m)
    logger.debug("download_layers_for_latlon: lat=%.6f lon=%.6f -> %s", lat, lon, bbox)
    return download_all_wms_layers(bbox=bbox, target_dir=target_dir)


def download_layers_default() -> List[str]:
    """
    Convenience für den 'kein lat/lon'-Fall: nutzt DEFAULT_BBOX und WMS_LAYERS_DIR.
    """
    logger.info("Nutze DEFAULT_BBOX und Standardzielordner.")
    return download_all_wms_layers(bbox=DEFAULT_BBOX, target_dir=WMS_LAYERS_DIR)
