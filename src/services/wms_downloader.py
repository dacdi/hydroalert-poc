# src/services/wms_downloader.py
from typing import Optional, List
from src.domain.models import BBox
from src.io.wms_client import build_wms_params, fetch_wms_png
from src.io.file_io import ensure_dir, save_png
from src.config.config import (
    WMS_LAYERS_DIR,
    WMS_BASE_URL,
    DEFAULT_BBOX,
    DEFAULT_SIZE,
    DEFAULT_LAYERS,
)
from src.utils.utils_logger import get_logger

logger = get_logger()

def download_all_wms_layers(
    bbox: Optional[BBox] = None,
    target_dir: Optional[str] = None,
) -> List[str]:
    """
    Lädt alle vordefinierten WMS-Layer und speichert sie als PNG.
    - bbox: überschreibt DEFAULT_BBOX (EPSG:25832)
    - target_dir: Zielordner; Standard ist WMS_LAYERS_DIR aus config
    """
    outdir = ensure_dir(target_dir or WMS_LAYERS_DIR)
    w, h = DEFAULT_SIZE
    use_bbox = bbox or DEFAULT_BBOX

    saved: List[str] = []
    for full_layer, short_name in DEFAULT_LAYERS.items():
        logger.info("⬇️ Downloading layer: %s", full_layer)
        params = build_wms_params(full_layer, use_bbox, w, h)
        content = fetch_wms_png(WMS_BASE_URL, params)
        path = save_png(content, outdir, short_name)
        saved.append(path)

    logger.info("✅ %d Layer gespeichert in %s", len(saved), outdir)
    return saved
